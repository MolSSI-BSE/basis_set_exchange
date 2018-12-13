'''
Add a basis set to the library
'''

import os
import copy
from ..fileio import write_json_basis
from ..misc import expand_elements
from . import read_formatted_basis

def add_basis(bs_file, data_dir, subdir, file_base, name, family, role, description, version, revision_description, refs=None, file_fmt=None):
    '''
    Add a basis set to this library

    Parameters
    ----------
    raw_file : str
        Path to the file with formatted basis set information
    subdir : str
        Subdirectory of the data directory to add the basis set to
    file_base : str
        Base name for new files
    name : str
        Name of the basis set
    family : str
        Family to which this basis set belongs
    role : str
        Role of the basis set (orbital, etc)
    description : str
        Description of the basis set
    version : str
        Version of the basis set
    revision_description : str
        Description of this version of the basis set
    refs : dict
        Mapping of references to elements
    file_fmt : str
        Format of the input basis data (None = autodetect)
    '''

    bs_data = read_formatted_basis(bs_file, file_fmt)
    bs_data['basis_set_description'] = description

    component_data = []
    done_elements = []

    # If refs are given, split up the file
    if refs is not None:
        if 'all' in refs:
            bs_data['basis_set_references'] = refs['all']
            component_data.append(bs_data)
        else:
            for k,v in refs.items():
                bs_tmp = copy.deepcopy(bs_data)
                elements = expand_elements(k, True)
                for e in elements:
                    if e in done_elements:
                        raise RuntimeError("Duplicate element in references dict: {}".format(e))

                bs_tmp['basis_set_elements'] = { x:y for x,y in bs_tmp['basis_set_elements'].items() if x in elements }
                bs_tmp['basis_set_references'] = v
                component_data.append(bs_tmp)
                done_elements.extend(elements)

    # Do any leftovers
    left_over = set(bs_data['basis_set_elements'].keys()) - set(done_elements)

    if len(left_over) > 0:
        bs_tmp = copy.deepcopy(bs_data)
        bs_tmp['basis_set_elements'] = { x:y for x,y in bs_tmp['basis_set_elements'].items() if x in left_over }
        bs_tmp['basis_set_references'] = []
        component_data.append(bs_tmp)
    
    # Create the component files
    # But keep track of elements for the element and table files
    el_file = {}
    for c in component_data:
        if len(c['basis_set_references']) > 0:
            filename = file_base + '_' + '_'.join(c['basis_set_references'])
        else:
            filename = file_base + '_noref'

        filename += '.' + str(version) + '.json'

        rel_path = os.path.join(subdir, filename)
        file_path = os.path.join(data_dir, rel_path) 
        if os.path.exists(file_path):
            raise RuntimeError("File {} already exists".format(file_path))

        write_json_basis(file_path, c)

        for el in c['basis_set_elements'].keys():
            if el in el_file:
                raise RuntimeError("Element already exists. This is a programming error")
 
            el_file[el] = {'element_components': [rel_path]}


    # Now create the element file
    elfile = { 
         "molssi_bse_schema": {
         "schema_type": "element",
         "schema_version": "0.1"
     },  
     "basis_set_name": name,
     "basis_set_description": description,
     "basis_set_elements": el_file 
    }

    element_file_name = '{}.{}.element.json'.format(file_base, version)
    element_file_relpath = os.path.join(subdir, element_file_name)
    element_file_path = os.path.join(data_dir, element_file_relpath)
    write_json_basis(element_file_path, elfile)

    # And the table basis
    tabfile = {
     "molssi_bse_schema": {
         "schema_type": "table",
         "schema_version": "0.1"
     },
     "basis_set_name": name,
     "basis_set_family": family,
     "basis_set_description": description,
     "basis_set_revision_description": revision_description,
     "basis_set_role": role,
     "basis_set_auxiliaries": {},
     "basis_set_elements": {k: {'element_entry': element_file_relpath} for k in bs_data['basis_set_elements'].keys()}
}

    # This gets created directly in the data directory
    tabfile_name = '{}.{}.table.json'.format(file_base, version)
    tabfile_path = os.path.join(data_dir, tabfile_name) 
    write_json_basis(tabfile_path, tabfile)
     


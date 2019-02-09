'''
Add a basis set to the library
'''

import os
from ..fileio import write_json_basis
from ..misc import expand_elements
from ..validator import validate_data
from .skel import create_skel
from .readers import read_formatted_basis
from .metadata import create_metadata_file


def add_basis(bs_file,
              data_dir,
              subdir,
              file_base,
              name,
              family,
              role,
              description,
              version,
              revision_description,
              refs=None,
              file_fmt=None):
    '''
    Add a basis set to this library

    This takes in a single file containing the basis set is some format, parses it, and
    create the component, element, and table basis set files in the given data_dir (and subdir).
    The metadata file for the basis is created if it doesn't exist, and the main metadata file is
    also updated.
    
    Parameters
    ----------
    bs_file : str
        Path to the file with formatted basis set information
    data_dir : str
        Path to the data directory to add the data to
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
    refs : dict or str
        Mapping of references to elements. This can be a dictionary with a compressed
        string of elements as keys and a list of reference strings as values.
        For example, {'H,Li-B,Kr': ['kumar2018a']}

        If a list or string is passed, then those reference(s) will be used for
        all elements.

        Elements that exist in the file but do not have a reference are given the
        usual 'noref' extension and the references entry is empty.
    file_fmt : str
        Format of the input basis data (None = autodetect)
    '''

    # Read the basis set data into a component file, and add the description
    bs_data = read_formatted_basis(bs_file, file_fmt)
    bs_data['basis_set_description'] = description

    if refs is None:
        component_data = [bs_data]
    else:
        # Split out the component data into files based on the reference
        # information. We keep track of which elements we've done so that
        # we can detect dupliates in the references (which would be an error)
        # (and also handle elements with no reference)
        orig_elements = bs_data['basis_set_elements']
        component_data = []
        done_elements = []

        # If a string or list of strings, use that as a reference for all elements
        if isinstance(refs, str):
            bs_data['basis_set_references'] = [refs]
            component_data.append(bs_data)
        elif isinstance(refs, list):
            bs_data['basis_set_references'] = refs
            component_data.append(bs_data)
        else:
            for k, v in refs.items():
                # Expand the string a list of integers (as strings)
                elements = expand_elements(k, True)

                # Make sure we have info for the given elements
                # and that there are no duplicates
                for el in elements:
                    if not el in orig_elements:
                        raise RuntimeError("Element {} not found in file {}".format(el, bs_file))
                    if el in done_elements:
                        raise RuntimeError("Duplicate element {} in reference string {}".format(el, k))

                # Shallow copy, then only include the given elements.
                # Set the ref, and keep track of the done elements
                bs_tmp = bs_data.copy()
                bs_tmp['basis_set_elements'] = {el: y for el, y in orig_elements.items() if el in elements}

                if isinstance(v, str):
                    bs_tmp['basis_set_references'] = [v]
                else:
                    bs_tmp['basis_set_references'] = v

                component_data.append(bs_tmp)
                done_elements.extend(elements)

            # Handle elements without a reference
            noref_elements = set(orig_elements.keys()) - set(done_elements)

            if len(noref_elements) > 0:
                bs_tmp = bs_data.copy()
                bs_tmp['basis_set_elements'] = {el: y for el, y in orig_elements.items() if el in noref_elements}
                bs_tmp['basis_set_references'] = []
                component_data.append(bs_tmp)

    # Start the data files for the element and table json
    element_file_data = create_skel('element')
    element_file_data['basis_set_name'] = name
    element_file_data['basis_set_description'] = description
    element_file_name = '{}.{}.element.json'.format(file_base, version)
    element_file_relpath = os.path.join(subdir, element_file_name)
    element_file_path = os.path.join(data_dir, element_file_relpath)

    table_file_data = create_skel('table')
    table_file_data['basis_set_revision_description'] = revision_description
    table_file_name = '{}.{}.table.json'.format(file_base, version)

    # and the metadata file
    meta_file_data = create_skel('metadata')
    meta_file_data['basis_set_name'] = name
    meta_file_data['basis_set_family'] = family
    meta_file_data['basis_set_description'] = description
    meta_file_data['basis_set_role'] = role
    meta_file_name = '{}.metadata.json'.format(file_base)

    # These get created directly in the top-level data directory
    table_file_path = os.path.join(data_dir, table_file_name)
    meta_file_path = os.path.join(data_dir, meta_file_name)

    # Can just make all the entries for the table file pretty easily
    table_file_entry = {'element_entry': element_file_relpath}
    table_file_data['basis_set_elements'] = {k: table_file_entry for k in bs_data['basis_set_elements'].keys()}

    # Create the filenames for the components
    # Also keep track of where data for each element is (for the element and table files)
    component_file_map = {}
    for cd in component_data:
        if len(cd['basis_set_references']) > 0:
            file_name = file_base + '_' + '_'.join(cd['basis_set_references'])
        else:
            file_name = file_base + '_noref'

        file_name += '.' + str(version) + '.json'
        file_relpath = os.path.join(subdir, file_name)
        file_path = os.path.join(data_dir, file_relpath)
        component_file_map[file_path] = cd

        # Add to the element file data
        # (we add the relative path to the location of the element file,
        # which resides in subdir)
        for el in cd['basis_set_elements'].keys():
            element_file_data['basis_set_elements'][el] = {'element_components': [file_relpath]}

    # Verify all data using the schema
    for file_path, file_data in component_file_map.items():
        validate_data('component', file_data)
    validate_data('element', element_file_data)
    validate_data('table', table_file_data)

    ######################################################################################
    # Before creating any files, check that all the files don't already exist.
    # Yes, there is technically a race condition (files could be created between the
    # check and then actually writing out), but if that happens, you are probably using
    # this library wrong
    #
    # Note that the metadata file may exist already. That is ok
    ######################################################################################
    for file_path in component_file_map.keys():
        if os.path.exists(file_path):
            raise RuntimeError("Component json file {} already exists".format(file_path))
    if os.path.exists(element_file_path):
        raise RuntimeError("Element json file {} already exists".format(element_file_path))
    if os.path.exists(table_file_path):
        raise RuntimeError("Table json file {} already exists".format(table_file_path))

    #############################################
    # Actually create all the files
    #############################################

    # First, create the subdirectory
    subdir_path = os.path.join(data_dir, subdir)
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)

    for file_path, file_data in component_file_map.items():
        write_json_basis(file_path, file_data)

    write_json_basis(element_file_path, element_file_data)
    write_json_basis(table_file_path, table_file_data)

    # Create the metadata file if it doesn't exist already
    if not os.path.exists(meta_file_path):
        write_json_basis(meta_file_path, meta_file_data)

    # Update the metadata file
    metadata_file = os.path.join(data_dir, 'METADATA.json')
    create_metadata_file(metadata_file, data_dir)

"""
Functions related to composing basis sets from individual components
"""

import os
from . import fileio, manip, memo

# If set to True, basis sets returned as python dictionaries
# will contain the path to a file where each shell/potential
# came from
debug_data_sources = False


def _whole_basis_harmonic(basis):
    '''
    Find whether an entire basis is cartesian, spherical, or if it is mixed

    May also return 'none' (as a string) if there are no electron shells (ie, ECP only)
    '''

    all_harm = set()

    for v in basis['basis_set_elements'].values():
        if not 'element_electron_shells' in v:
            return "none"
        for sh in v['element_electron_shells']:
            all_harm.add(sh['shell_harmonic_type'])

    if len(all_harm) > 1:
        return 'mixed'
    else:
        return all_harm.pop()


def compose_elemental_basis(file_relpath, data_dir):
    """
    Creates an 'elemental' basis from an elemental json file

    This function reads the info from the given file, and reads all the component
    basis set information from the files listed therein. It then composes all the
    information together into one 'elemental' basis dictionary
    """

    # Do a simple read of the json
    el_bs = fileio.read_json_basis(os.path.join(data_dir, file_relpath))

    # construct a list of all files to read
    component_files = set()
    for k, v in el_bs['basis_set_elements'].items():
        component_files.update(set(v['element_components']))

    # Read all the data from these files into a big dictionary
    component_map = {k: fileio.read_json_basis(os.path.join(data_dir, k)) for k in component_files}

    # If debugging, add file source info
    if debug_data_sources:
        for k, v in component_map.items():
            for el, el_data in v['basis_set_elements'].items():
                if 'element_electron_shells' in el_data:
                    for sh in el_data['element_electron_shells']:
                        sh['data_source'] = os.path.join(data_dir, k)
                if 'element_ecp' in el_data:
                    for sh in el_data['element_ecp']:
                        sh['data_source'] = os.path.join(data_dir, k)

    # Broadcast the basis_set_references to each element
    # Use the basis_set_description for the reference description
    for k, v in component_map.items():
        for el, el_data in v['basis_set_elements'].items():
            el_data['element_references'] = [{
                'reference_description': v['basis_set_description'],
                'reference_keys': v['basis_set_references']
            }]

    # Compose on a per-element basis
    for k, v in el_bs['basis_set_elements'].items():

        components = v.pop('element_components')

        # all of the component data for this element
        el_comp_data = [component_map[c]['basis_set_elements'][k] for c in components]

        # merge all the data
        v = manip.merge_element_data(v, el_comp_data)
        el_bs['basis_set_elements'][k] = v

    return el_bs


@memo.BSEMemoize
def compose_table_basis(file_relpath, data_dir):
    """
    Creates a 'table' basis from an table json file

    This function reads the info from the given file, and reads all the elemental
    basis set information from the files listed therein. It then composes all the
    information together into one 'table' basis dictionary
    """

    # Do a simple read of the json
    file_path = os.path.join(data_dir, file_relpath)
    table_bs = fileio.read_json_basis(file_path)

    # construct a list of all elemental files to read
    element_files = set()
    for v in table_bs['basis_set_elements'].values():
        element_files.add(v['element_entry'])

    # Create a map of the elemental basis data
    # (maps file path to data contained in that file)
    element_map = {k: compose_elemental_basis(k, data_dir) for k in element_files}

    # Replace the basis set for all elements in the table basis with the data
    # from the elemental basis
    for k, v in table_bs['basis_set_elements'].items():
        entry = v['element_entry']
        data = element_map[entry]

        table_bs['basis_set_elements'][k] = data['basis_set_elements'][k]

    # Add the version to the dictionary
    file_base = os.path.basename(file_relpath)
    table_bs['basis_set_version'] = file_base.split('.')[-3]

    # Add whether the entire basis is spherical or cartesian
    table_bs['basis_set_harmonic_type'] = _whole_basis_harmonic(table_bs)

    # Read and merge in the metadata
    # This file must be in the same location as the table file
    meta_dirpath, table_filename = os.path.split(file_path)
    meta_filename = table_filename.split('.')[0] + '.metadata.json'
    meta_filepath = os.path.join(meta_dirpath, meta_filename)
    bs_meta = fileio.read_json_basis(meta_filepath)
    table_bs.update(bs_meta)

    # Remove the molssi schema (which isn't needed here)
    table_bs.pop('molssi_bse_schema')

    return table_bs

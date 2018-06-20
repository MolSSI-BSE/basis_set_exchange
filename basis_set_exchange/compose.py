"""
Functions related to composing basis sets from individual components
"""

import os

from . import fileio
from . import manip
from . import memo


def compose_elemental_basis(file_path):
    """
    Creates an 'elemental' basis from an elemental json file

    This function reads the info from the given file, and reads all the component
    basis set information from the files listed therein. It then composes all the
    information together into one 'elemental' basis dictionary
    """

    # Where to look for components (should be relative to the parent
    # of the given file_path)
    data_dir = os.path.dirname(file_path)
    data_dir = os.path.dirname(data_dir)

    # Do a simple read of the json
    el_bs = fileio.read_json_basis(file_path)

    # construct a list of all files to read
    component_names = set()
    for k, v in el_bs['basis_set_elements'].items():
        component_names.update(set(v['element_components']))

    # Read all the data from these files into a big dictionary
    component_map = {k: fileio.read_json_basis(os.path.join(data_dir, k)) for k in component_names}

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
def compose_table_basis(file_path):
    """
    Creates a 'table' basis from an table json file

    This function reads the info from the given file, and reads all the elemental
    basis set information from the files listed therein. It then composes all the
    information together into one 'table' basis dictionary
    """

    # Where to look for components (should be relative to the directory
    # of the given file_path)
    data_dir = os.path.dirname(file_path)

    # Do a simple read of the json
    table_bs = fileio.read_json_basis(file_path)

    # construct a list of all elemental files to read
    component_names = set()
    for k, v in table_bs['basis_set_elements'].items():
        component_names.add(v['element_entry'])

    # Create a map of the elemental basis data
    element_map = {k: compose_elemental_basis(os.path.join(data_dir, k)) for k in component_names}

    for k, v in table_bs['basis_set_elements'].items():
        entry = v['element_entry']
        data = element_map[entry]

        # Replace the basis set for this element with the one
        # from the elemental basis
        table_bs['basis_set_elements'][k] = data['basis_set_elements'][k]

    # Add the version to the dictionary
    file_base = os.path.basename(file_path)
    table_bs['basis_set_version'] = file_base.split('.')[-3]

    return table_bs

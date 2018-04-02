"""
Functions related to composing full basis sets from individual components
"""

import os
from . import manip
from . import io


def compose_elemental_basis(file_path):
    """
    Creates an 'elemental' basis from an elemental json file

    This function reads the info from the given path, and reads all the component
    basis set information from the files listed there. It then composes all the
    information together into one 'elemental' basis dictionary
    """

    # Where to look for components (should be relative to the parent
    # of the given file_path)
    data_dir = os.path.dirname(file_path)
    data_dir = os.path.dirname(data_dir)

    # Do a simple read of the json
    js = io.read_json_basis(file_path)

    # construct a list of all files to read
    # TODO - can likely be replaced by memoization
    component_names = set()
    for k, v in js['basis_set_elements'].items():
        component_names.update(set(v['element_components']))

    component_map = {k: io.read_json_basis(os.path.join(data_dir, k)) for k in component_names}

    # Broadcast the basis_set_references to each element
    for k, v in component_map.items():
        for el, el_data in v['basis_set_elements'].items():
            el_data['element_references'] = v['basis_set_references']

    # Compose on a per-element basis
    for k, v in js['basis_set_elements'].items():

        # Also removes 'element_components' from the dict
        components = v.pop('element_components')

        # all of the component data for this element
        el_data = [component_map[c]['basis_set_elements'][k] for c in components]

        # start with an empty shell list, and merge in all the data
        v['element_electron_shells'] = []
        v = manip.merge_element_data(v, el_data)

        # Set it in the actual dict (v was a reference before)
        js['basis_set_elements'][k] = v

    return js


def compose_table_basis(file_path):
    """
    Creates a full 'table' basis from an table json file

    This function reads the info from the given path, and reads all the elemental
    basis set information from the files listed there. It then composes all the
    information together into one 'table' basis dictionary
    """

    # Where to look for components (should be relative to the directory
    # of the given file_path)
    data_dir = os.path.dirname(file_path)

    # Do a simple read of the json
    js = io.read_json_basis(file_path)

    # construct a list of all files to read
    # TODO - can likely be replaced by memoization
    component_names = set()
    for k, v in js['basis_set_elements'].items():
        component_names.add(v['element_entry'])

    # Create a map of the elemental bases
    element_map = {k: compose_elemental_basis(os.path.join(data_dir, k)) for k in component_names}

    for k, v in js['basis_set_elements'].items():
        entry = v['element_entry']
        data = element_map[entry]

        # Replace the basis set for this element with the one
        # from the elemental basis
        js['basis_set_elements'][k] = data['basis_set_elements'][k]

    return js

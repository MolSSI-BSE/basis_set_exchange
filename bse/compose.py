
import os
from . import manip
from . import io


def compose_elemental_basis(file_path):
    data_dir = os.path.dirname(file_path)
    js = io.read_json_basis(file_path)

    # construct a list of all files to read
    # TODO - can likely be replaced by memoization
    component_names = set()
    for k, v in js['basisSetElements'].items():
        component_names.update(set(v['elementComponents']))

    component_map = {k: io.read_json_basis(os.path.join(data_dir, k)) for k in component_names}

    for k, v in js['basisSetElements'].items():

        components = v['elementComponents']

        v['elementElectronShells'] = []

        # all of the component data for this element
        el_data = [component_map[c]['basisSetElements'][k] for c in components]

        v = manip.merge_element_data(v, el_data)

        # Remove the 'elementComponents' now that the data has been inserted
        v.pop('elementComponents')

        # Set it in the actual dict (v was a reference before)
        js['basisSetElements'][k] = v

    return js


def compose_table_basis(file_path):
    data_dir = os.path.dirname(file_path)
    js = io.read_json_basis(file_path)

    # construct a list of all files to read
    # TODO - can likely be replaced by memoization
    component_names = set()
    for k, v in js['basisSetElements'].items():
        component_names.add(v['elementEntry'])

    component_map = {k: compose_elemental_basis(os.path.join(data_dir, k)) for k in component_names}

    for k, v in js['basisSetElements'].items():
        entry = v['elementEntry']
        data = component_map[entry]

        # Replace the basis set for this element with the one
        # from the elemental basis
        js['basisSetElements'][k] = data['basisSetElements'][k]

    return js




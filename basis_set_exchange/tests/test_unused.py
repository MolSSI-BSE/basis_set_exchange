'''
Test for unused data
'''

import os
import basis_set_exchange as bse
from .common_testvars import data_dir, all_component_files, all_element_files, all_table_files, bs_metadata


def test_unused_data():
    '''
    Test for any unused data in the data directory
    '''

    # All elements contained in all component files
    all_component_elements = {}
    for cf in all_component_files:
        cpath = os.path.join(data_dir, cf)
        cdata = bse.fileio.read_json_basis(cpath)
        all_component_elements[cpath] = list(cdata['basis_set_elements'].keys())

    # All elements contained in all element files
    # And all element data as read from the file
    all_element_elements = {}
    all_element_data = {}
    for ef in all_element_files:
        efpath = os.path.join(data_dir, ef)
        efdata = bse.fileio.read_json_basis(efpath)
        all_element_elements[efpath] = list(efdata['basis_set_elements'].keys())
        all_element_data[efpath] = efdata['basis_set_elements']

    # Now go through what is reachable through a table file
    for tfile in all_table_files:
        table_path = os.path.join(data_dir, tfile)
        table_data = bse.fileio.read_json_basis(table_path)

        # What element files are linked to this table file
        el_files = [(k, v['element_entry']) for k, v in table_data['basis_set_elements'].items()]

        # Loop over the element files, and remove the corresponding entry
        # from all_component_elements
        for el, el_file in el_files:
            el_file_path = os.path.join(data_dir, el_file)
            el_file_data = all_element_data[el_file_path]

            for cfile in el_file_data[el]['element_components']:
                cfile_path = os.path.join(data_dir, cfile)
                if el in all_component_elements[cfile_path]:
                    all_component_elements[cfile_path].remove(el)

            # Now remove the corresponding entry from all_element_elements
            if el in all_element_elements[el_file_path]:
                all_element_elements[el_file_path].remove(el)

    # See which ones were unused
    found_unused = False

    # Merge into one big dictionary
    remaining = all_component_elements
    remaining.update(all_element_elements)

    for k, v in remaining.items():
        if len(v) == 0:
            continue

        found_unused = True
        for el in v:
            print("Element {:3} in {} not used".format(el, k))

    if found_unused:
        raise RuntimeError("Found unused data")

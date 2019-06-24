'''
Test for unused data
'''

import os
import basis_set_exchange as bse
from .common_testvars import data_dir, all_component_paths, all_element_paths, all_table_paths, all_metadata_files, all_families


def test_unused_data():
    '''
    Test for any unused data in the data directory
    '''

    # All elements contained in all component files
    all_component_elements = {}
    for component_path in all_component_paths:
        component_data = bse.fileio.read_json_basis(component_path)
        all_component_elements[component_path] = list(component_data['elements'].keys())

    # All elements contained in all element files
    # And all element data as read from the file
    all_element_elements = {}
    all_element_data = {}
    for element_path in all_element_paths:
        element_data = bse.fileio.read_json_basis(element_path)
        all_element_elements[element_path] = list(element_data['elements'].keys())
        all_element_data[element_path] = element_data['elements']

    # Now go through what is reachable through a table file
    for table_path in all_table_paths:
        table_data = bse.fileio.read_json_basis(table_path)

        # What element files are linked to this table file
        el_files = list(table_data['elements'].items())

        # Loop over the element files, and remove the corresponding entry
        # from all_component_elements
        for el, el_file in el_files:
            # Normalize the paths (since we will be removing them later)
            el_file = os.path.normpath(el_file)
            el_file_path = os.path.join(data_dir, el_file)


            el_file_data = all_element_data[el_file_path]

            for cfile in el_file_data[el]['components']:
                cfile = os.path.normpath(cfile)
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


def test_unused_notes():
    '''
    Test for orphan basis and family notes files
    '''

    all_basis_notes = []
    all_family_notes = []
    for root, dirs, files in os.walk(data_dir):
        for basename in files:
            fpath = os.path.join(root, basename)
            fpath = os.path.relpath(fpath, data_dir)

            if basename.endswith('.notes'):
                all_basis_notes.append(fpath)
            elif basename.startswith('NOTES.'):
                all_family_notes.append(fpath)

    found_unused = False
    for bs_notes in all_basis_notes:
        base = os.path.splitext(bs_notes)[0]
        metafile = base + '.metadata.json'
        if metafile not in all_metadata_files:
            print("File {} does not have a corresponding metadata file".format(bs_notes))
            found_unused = True

    for fam_notes in all_family_notes:
        fam = os.path.splitext(fam_notes)[1][1:] # Removes period
        if fam not in all_families:
            print("File {} does not have a corresponding family".format(fam_notes))
            found_unused = True

    if found_unused:
        raise RuntimeError("Found unused notes files")

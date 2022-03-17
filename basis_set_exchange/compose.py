# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Functions related to composing basis sets from individual components
"""

import os
from . import fileio, manip, memo


def _whole_basis_types(basis):
    '''
    Get a list of all the types of features in this basis set.

    '''

    all_types = set()

    for v in basis['elements'].values():
        if 'electron_shells' in v:
            for sh in v['electron_shells']:
                all_types.add(sh['function_type'])

        if 'ecp_potentials' in v:
            for pot in v['ecp_potentials']:
                all_types.add(pot['ecp_type'])

    return sorted(all_types)


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
    for k, v in el_bs['elements'].items():
        component_files.update(set(v['components']))

    # Read all the data from these files into a big dictionary
    component_map = {k: fileio.read_json_basis(os.path.join(data_dir, k)) for k in component_files}

    # Use the basis_set_description for the reference description
    for k, v in component_map.items():
        for el, el_data in v['elements'].items():
            el_data['references'] = [{
                'reference_description': v['description'],
                'reference_keys': el_data['references']
            }]

    # Compose on a per-element basis
    for k, v in el_bs['elements'].items():

        components = v.pop('components')

        # all of the component data for this element
        el_comp_data = []
        for c in components:
            centry = component_map[c]['elements']

            if k not in centry:
                raise RuntimeError('File {} does not contain element {}'.format(c, k))

            el_comp_data.append(centry[k])

        # merge all the data
        v = manip.merge_element_data(None, el_comp_data)
        el_bs['elements'][k] = v

    return el_bs


@memo.BSEMemoize
def compose_table_basis(file_relpath, data_dir):
    """
    Creates a 'table' basis from an table json file

    This function reads the info from the given file, and reads all the elemental
    basis set information from the files listed therein. It then composes all the
    information together into one 'table' basis dictionary

    Note that the data returned from this function will not be shared, even if
    the function is called again with the same arguments.
    """

    # Do a simple read of the json
    file_path = os.path.join(data_dir, file_relpath)
    table_bs = fileio.read_json_basis(file_path)

    # construct a list of all elemental files to read
    element_files = set(table_bs['elements'].values())

    # Create a map of the elemental basis data
    # (maps file path to data contained in that file)
    element_map = {k: compose_elemental_basis(k, data_dir) for k in element_files}

    # Replace the basis set for all elements in the table basis with the data
    # from the elemental basis
    for k, entry in table_bs['elements'].items():
        data = element_map[entry]

        if k not in data['elements']:
            raise KeyError('File {} does not contain element {}'.format(entry, k))

        table_bs['elements'][k] = data['elements'][k]

    # Add the version to the dictionary
    file_base = os.path.basename(file_relpath)
    table_bs['version'] = file_base.split('.')[-3]

    # Add whether the entire basis is spherical or cartesian
    table_bs['function_types'] = _whole_basis_types(table_bs)

    # Read and merge in the metadata
    # This file must be in the same location as the table file
    meta_dirpath, table_filename = os.path.split(file_path)
    meta_filename = table_filename.split('.')[0] + '.metadata.json'
    meta_filepath = os.path.join(meta_dirpath, meta_filename)
    bs_meta = fileio.read_json_basis(meta_filepath)
    table_bs.update(bs_meta)

    # Modify the molssi schema (is now 'complete' and not 'table')
    table_bs['molssi_bse_schema'] = {"schema_type": "complete", "schema_version": "0.1"}

    return table_bs

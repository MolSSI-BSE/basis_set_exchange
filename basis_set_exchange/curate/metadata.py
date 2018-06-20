'''
Helpers for handling BSE metadata
'''

import os
from collections import OrderedDict

from .. import api
from .. import compose
from .. import fileio


def create_metadata_file(output_path, data_dir):
    '''Creates a METADATA.json file from a data directory

    The file is written to output_path
    '''

    basis_filelist = fileio.get_basis_filelist(data_dir)

    metadata = {}
    for bs_file_path in basis_filelist:
        filename = os.path.split(bs_file_path)[1]

        filebase = os.path.splitext(filename)[0]  # remove .json
        filebase = os.path.splitext(filebase)[0]  # remove .table
        filebase = os.path.splitext(filebase)[0]  # remove .version

        # Fully compose the basis set from components
        bs = compose.compose_table_basis(bs_file_path)

        # Prepare the metadata
        tr_name = api.transform_basis_name(bs['basis_set_name'])
        display_name = bs['basis_set_name']
        defined_elements = sorted(list(bs['basis_set_elements'].keys()), key=lambda x: int(x))
        description = bs['basis_set_description']
        revision_desc = bs['basis_set_revision_description']
        role = bs['basis_set_role']
        family = bs['basis_set_family']
        auxiliaries = bs['basis_set_auxiliaries']

        function_types = set()
        for e in bs['basis_set_elements'].values():
            if 'element_electron_shells' in e:
                for s in e['element_electron_shells']:
                    function_types.add(s['shell_function_type'])
            if 'element_ecp' in e:
                function_types.add('ecp')

        function_types = sorted(list(function_types))

        # convert the file path to the internal identifier for the basis set
        internal_name = os.path.basename(bs_file_path)
        internal_name = internal_name.replace(".table.json", "")

        # split out the version number
        internal_name, ver = os.path.splitext(internal_name)
        ver = ver[1:]

        single_meta = OrderedDict([('display_name', display_name), ('filebase', filebase), ('family', family),
                                   ('description', description), ('revdesc', revision_desc), ('role', role),
                                   ('auxiliaries', auxiliaries), ('functiontypes',
                                                                  function_types), ('elements', defined_elements)])

        if not tr_name in metadata:
            metadata[tr_name] = {'versions': {ver: single_meta}}
        else:
            metadata[tr_name]['versions'][ver] = single_meta

    # sort the versions and find the max version
    # Also place display_name, role, auxiliaries into the top level for this basis
    for k, v in metadata.items():
        latest = max(v['versions'].keys())
        latest_data = v['versions'][latest]
        metadata[k] = OrderedDict(
            [('display_name', latest_data['display_name']), ('filebase', latest_data['filebase']), ('latest_version',
                                                                                                    latest),
             ('family', latest_data['family']), ('role', latest_data['role']), ('functiontypes',
                                                                                latest_data['functiontypes']),
             ('auxiliaries', latest_data['auxiliaries']), ('versions', OrderedDict(sorted(v['versions'].items())))])

    # Remove these from under versions
    to_remove = ['display_name', 'role', 'auxiliaries', 'family', 'filebase', 'functiontypes']
    for v in metadata.values():
        for ver in v['versions'].values():
            for x in to_remove:
                ver.pop(x)

    # Write out the metadata
    metadata = OrderedDict(sorted(list(metadata.items())))
    fileio._write_plain_json(output_path, metadata)

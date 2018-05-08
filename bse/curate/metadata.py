'''
Main interface to BSE functionality
'''

import os
import json
import codecs
from collections import OrderedDict
from .. import io
from .. import compose
from .. import manip


def create_metadata_file(output_path, data_dir):

    basis_filelist = io.get_basis_filelist(data_dir)

    metadata = {}
    for bs_file_path in basis_filelist:
        filename = os.path.split(bs_file_path)[1]

        # Fully compose the basis set from components
        bs = compose.compose_table_basis(bs_file_path)

        # Prepare the metadata
        tr_name = manip.transform_basis_name(bs['basis_set_name'])
        displayname = bs['basis_set_name']
        defined_elements = sorted(list(bs['basis_set_elements'].keys()))
        description = bs['basis_set_description']
        revision_desc = bs['basis_set_revision_description']

        function_types = set()
        for e in bs['basis_set_elements'].values():
            if 'element_electron_shells' in e:
                for s in e['element_electron_shells']:
                    function_types.add(s['shell_function_type'])
            if 'element_ecp' in e:
                function_types.add('ECP')

        function_types = sorted(list(function_types))

        # convert the file path to the internal identifier for the basis set
        internal_name = os.path.basename(bs_file_path)
        internal_name = internal_name.replace(".table.json", "")

        # split out the version number
        internal_name, ver = os.path.splitext(internal_name)
        ver = int(ver[1:])

        single_meta = OrderedDict([('displayname', displayname),
                                   ('filename', filename), ('description', description), ('revdesc', revision_desc),
                                   ('functiontypes', function_types), ('elements', defined_elements)])

        if not tr_name in metadata:
            metadata[tr_name] = {'versions': {ver: single_meta}}
        else:
            metadata[tr_name]['versions'][ver] = single_meta

    # sort the versions and find the max version
    for k, v in metadata.items():
        metadata[k] = OrderedDict([('latest_version', max(v['versions'].keys())),
                                   ('versions', OrderedDict(sorted(v['versions'].items())))])

    # Write out the metadata
    metadata = OrderedDict(sorted(list(metadata.items())))
    with codecs.open(output_path, 'w', 'utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

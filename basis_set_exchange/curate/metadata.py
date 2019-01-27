'''
Helpers for handling BSE metadata
'''

import os
from collections import OrderedDict

from ..compose import compose_table_basis
from ..fileio import get_all_filelist, _write_plain_json
from ..misc import transform_basis_name


def create_metadata_file(output_path, data_dir):
    '''Creates a METADATA.json file from a data directory

    The file is written to output_path
    '''

    basis_filelist = get_all_filelist(data_dir)[1]

    metadata = {}
    for bs_file_relpath in basis_filelist:
        # Path to the table file (relative to data_dir)
        # metadata files and table files for all versions should be in the
        # same location
        # Also obtain the filename of the table file
        table_relpath, table_filename = os.path.split(bs_file_relpath)

        # Obtain the base filename and version from the filename
        # The base filename is the part before the first period
        # (filebase.ver.table.json)
        table_filebase, ver, _, _ = table_filename.split('.')

        # Fully compose the basis set from components
        bs = compose_table_basis(bs_file_relpath, data_dir)

        # Prepare the metadata
        tr_name = transform_basis_name(bs['basis_set_name'])
        defined_elements = sorted(list(bs['basis_set_elements'].keys()), key=lambda x: int(x))

        # Determine the types of functions contained in the basis
        # (gto, ecp, etc)
        function_types = set()
        for e in bs['basis_set_elements'].values():
            if 'element_electron_shells' in e:
                for s in e['element_electron_shells']:
                    function_types.add(s['shell_function_type'])
            if 'element_ecp' in e:
                function_types.add('ecp')

        function_types = sorted(list(function_types))

        # Create the metadata for this specific version
        # yapf: disable
        version_meta = OrderedDict([('file_relpath', bs_file_relpath),
                                    ('revdesc', bs['basis_set_revision_description']),
                                    ('elements', defined_elements)])
        # yapf: enable

        # Add to the full metadata dict
        if not tr_name in metadata:
            # Create a new entry, with all the common metadata at the top
            # for this entry
            # yapf: disable
            metadata[tr_name] = OrderedDict([
                                 ('display_name', bs['basis_set_name']),
                                 ('description', bs['basis_set_description']),
                                 ('latest_version', None),
                                 ('basename', table_filebase),
                                 ('relpath', table_relpath),
                                 ('family', bs['basis_set_family']),
                                 ('role', bs['basis_set_role']),
                                 ('functiontypes', function_types),
                                 ('auxiliaries', bs['basis_set_auxiliaries']),
                                 ('versions', {ver: version_meta})])
            # yapf: enable

        else:
            # There is an existing entry. Make sure
            # file basename, filename, and functiontypes match
            if metadata[tr_name]['functiontypes'] != function_types:
                raise RuntimeError("Function types do not match across versions for " + tr_name)
            if metadata[tr_name]['basename'] != table_filebase:
                raise RuntimeError("File basenames do not match across versions for " + tr_name)
            if metadata[tr_name]['relpath'] != table_relpath:
                raise RuntimeError("Basis directories do not match across versions for " + tr_name)

            metadata[tr_name]['versions'][ver] = version_meta

    # sort the versions and find the max version
    for k, v in metadata.items():
        latest = max(v['versions'].keys())
        metadata[k]['latest_version'] = latest

        # Reorder the versions (may have been read out of order)
        metadata[k]['versions'] = OrderedDict(sorted(v['versions'].items()))

    # Write out the metadata
    metadata = OrderedDict(sorted(list(metadata.items())))
    _write_plain_json(output_path, metadata)

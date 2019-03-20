'''
Helpers for handling BSE metadata
'''

import os

from ..compose import compose_table_basis
from ..fileio import get_all_filelist, read_json_basis, _write_plain_json
from ..misc import transform_basis_name


def create_metadata_file(output_path, data_dir):
    '''Creates a METADATA.json file from a data directory

    The file is written to output_path
    '''

    # Relative path to all (BASIS).metadata.json files
    meta_filelist, table_filelist, _, _ = get_all_filelist(data_dir)

    metadata = {}
    for meta_file_relpath in meta_filelist:

        # Read in the metadata for a single basis set
        meta_file_path = os.path.join(data_dir, meta_file_relpath)
        bs_metadata = read_json_basis(meta_file_path)

        # Base of the filename for table basis sets
        # Basename is something like '6-31G.', including the last period
        base_relpath, meta_filename = os.path.split(meta_file_relpath)
        base_filename = meta_filename.split('.')[0] + '.'

        # All the table files that correspond to this metadata file
        # (relative to data_dir)

        this_filelist = [
            x for x in table_filelist
            if os.path.dirname(x) == base_relpath and os.path.basename(x).startswith(base_filename)
        ]

        # The 'versions' dict that will go into the metadata
        version_info = {}

        # Make sure function types are the same
        function_types = None

        # For each table basis, compose it
        for table_file in this_filelist:
            # Obtain just the filename of the table basis
            table_filename = os.path.basename(table_file)

            # Obtain the base filename and version from the filename
            # The base filename is the part before the first period
            # (filebase.ver.table.json)
            table_filebase, ver, _, _ = table_filename.split('.')

            # Fully compose the basis set from components
            bs = compose_table_basis(table_file, data_dir)

            # Elements for which this basis is defined
            defined_elements = sorted(list(bs['elements'].keys()), key=lambda x: int(x))

            # Determine the types of functions contained in the basis
            # (gto, ecp, etc)
            if function_types is None:
                function_types = bs['function_types']
            elif function_types != bs['function_types']:
                raise RuntimeError("Differing function types across versions for " + base_filename)

            # Create the metadata for this specific version
            # yapf: disable
            version_info[ver] = { 'file_relpath': table_file,
                                  'revdesc': bs['revision_description'],
                                  'elements': defined_elements
                                }
            # yapf: enable

        # Sort the version dicts
        version_info = dict(sorted(version_info.items()))
        # Find the maximum version for this basis
        latest_ver = max(version_info.keys())

        # Create the common metadata for this basis set
        # display_name and other_names are placeholders to keep order
        # yapf: disable
        common_md = { 'display_name': None,
                      'other_names': None,
                      'description': bs['description'],
                      'latest_version': latest_ver,
                      'basename': base_filename[:-1], # Strip off that trailing period
                      'relpath': base_relpath,
                      'family': bs['family'],
                      'role': bs['role'],
                      'functiontypes': function_types,
                      'auxiliaries': bs['auxiliaries'],
                      'versions': version_info }
        # yapf: enable

        # Loop through all the common names, translate them, and then add the data
        for bs_name in bs_metadata['names']:
            tr_name = transform_basis_name(bs_name)

            if tr_name in metadata:
                raise RuntimeError("Duplicate basis set name: " + tr_name)

            # Create a new entry, with all the common metadata
            # Also, store the other names for this basis
            other_names = bs_metadata['names'].copy()
            other_names.remove(bs_name)
            metadata[tr_name] = common_md.copy()
            metadata[tr_name]['display_name'] = bs_name
            metadata[tr_name]['other_names'] = other_names

    # Write out the metadata
    metadata = dict(sorted(metadata.items()))
    _write_plain_json(output_path, metadata)

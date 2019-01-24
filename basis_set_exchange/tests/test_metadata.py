"""
Tests for BSE metadata
"""

import tempfile
import json
import os
import pytest

from basis_set_exchange import api, curate, fileio
from .common_testvars import data_dir, all_table_files, all_metadata_files


def test_get_metadata():
    '''Test the get_metadata function in the API'''

    api.get_metadata(data_dir)


def test_metadata_uptodate():
    '''Tests that the METADATA.json file is up to date'''

    old_metadata = os.path.join(data_dir, 'METADATA.json')

    # Create a temporary file
    new_metadata_tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    new_metadata = new_metadata_tmp.name
    new_metadata_tmp.close()

    curate.create_metadata_file(new_metadata, data_dir)

    with open(old_metadata, 'r') as f:
        old_data = json.load(f)
    with open(new_metadata, 'r') as f:
        new_data = json.load(f)

    os.remove(new_metadata)

    assert old_data == new_data


@pytest.mark.parametrize('meta_file_path', all_metadata_files)
def test_basis_metadata(meta_file_path):
    '''Test that each metadata file is paired with a table basis
       in the same directory
    '''
    pass

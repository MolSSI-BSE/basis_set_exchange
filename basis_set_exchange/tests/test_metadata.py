"""
Tests for BSE metadata
"""

import json
import os
import pytest
import glob

from basis_set_exchange import api, curate, fileio
from .common_testvars import data_dir, all_table_files, all_metadata_files


def test_get_metadata():
    '''Test the get_metadata function in the API'''

    api.get_metadata(data_dir)


def test_metadata_uptodate(tmp_path):
    '''Tests that the METADATA.json file is up to date'''

    tmp_path = str(tmp_path)  # Needed for python 3.5
    old_metadata = os.path.join(data_dir, 'METADATA.json')

    # Create a temporary file
    new_metadata = os.path.join(tmp_path, 'NEW_METADATA.json')

    curate.create_metadata_file(str(new_metadata), data_dir)

    with open(old_metadata, 'r') as f:
        old_data = json.load(f)
    with open(new_metadata, 'r') as f:
        new_data = json.load(f)

    assert old_data == new_data


@pytest.mark.parametrize('meta_file_path', all_metadata_files)
def test_basis_metadata_pair1(meta_file_path):
    '''Test that each metadata file is paired with a table basis
       in the same directory
    '''

    bsname = os.path.basename(meta_file_path).split('.')[0]
    meta_subdir = os.path.dirname(meta_file_path)
    test_path = os.path.join(data_dir, meta_subdir, bsname)
    test_files = glob.glob(test_path + '.*.table.json')
    assert len(test_files) > 0


@pytest.mark.parametrize('table_file_path', all_table_files)
def test_basis_metadata_pair2(table_file_path):
    '''Test that each table basis is paired with a metadata file
       in the same directory
    '''

    bsname = os.path.basename(table_file_path).split('.')[0]
    table_subdir = os.path.dirname(table_file_path)
    test_file = os.path.join(data_dir, table_subdir, bsname) + '.metadata.json'
    assert os.path.isfile(test_file)

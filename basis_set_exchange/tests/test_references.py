"""
Tests for reference handling
"""

import json
import os
import pytest

from basis_set_exchange import api, validator, fileio
from .common_testvars import data_dir, all_component_files


@pytest.mark.parametrize('file_path', all_component_files)
def test_filenames(file_path):
    '''
    Test that component filenames end with the correct reference
    '''
    full_path = os.path.join(data_dir, file_path)
    with open(full_path, 'r') as f:
        file_refs = json.load(f)['basis_set_references']
        if len(file_refs) > 0:
            ref_str = '_'.join(file_refs)
        else:
            ref_str = 'noref'
        ref_str = '_' + ref_str

        # Strip off '.0.json', '.1.json', etc
        base_name = os.path.splitext(file_path)[0]
        base_name = os.path.splitext(base_name)[0]

        # Base name should end with the reference string
        print(base_name)
        print(ref_str)
        assert base_name.endswith(ref_str)


def test_valid_reffile():
    '''
    Test to make sure the references file is valid
    '''
    full_path = os.path.join(data_dir, "REFERENCES.json")
    validator.validate_file('references', full_path)

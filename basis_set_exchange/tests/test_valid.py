"""
Test for validating the formatting of the json files
"""

import glob
import os

import pytest
from basis_set_exchange import api, validator, fileio

_data_dir = api._default_data_dir
_all_files = fileio.get_all_filelist(_data_dir)

@pytest.mark.parametrize('file_path', _all_files[0])
def test_valid_table(file_path):
    full_path = os.path.join(_data_dir, file_path)
    validator.validate_file('table', full_path)

@pytest.mark.parametrize('file_path', _all_files[1])
def test_valid_element(file_path):
    full_path = os.path.join(_data_dir, file_path)
    validator.validate_file('element', full_path)

@pytest.mark.parametrize('file_path', _all_files[2])
def test_valid_component(file_path):
    full_path = os.path.join(_data_dir, file_path)
    validator.validate_file('component', full_path)

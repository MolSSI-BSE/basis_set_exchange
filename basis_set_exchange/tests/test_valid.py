"""
Test for validating the formatting of the json files
"""

import glob
import os

import pytest
from basis_set_exchange import api, validator

_data_dir = api._default_data_dir

_all_files = glob.glob(os.path.join(_data_dir, '*.json'))
_all_files.extend(glob.glob(os.path.join(_data_dir, '*', '*.json')))

@pytest.mark.parametrize('file_path', _all_files)
def test_valid(file_path):
    # Validate all the data files in the data directory
    # against their respective schemas
    if file_path.endswith('METADATA.json'):
        return
    if file_path.endswith('REFERENCES.json'):
        validator.validate('references', file_path)
    elif file_path.endswith('.table.json'):
        validator.validate('table', file_path)
    elif file_path.endswith('.element.json'):
        validator.validate('element', file_path)
    else:
        validator.validate('component', file_path)

"""
Test for validating the formatting of the json files
"""

import glob
import os

import pytest
from basis_set_exchange import api, validator, fileio

_data_dir = api._default_data_dir

_all_files = []
for x in fileio.get_all_filelist(_data_dir):
    _all_files.extend(x)

@pytest.mark.parametrize('file_path', _all_files)
def test_valid(file_path):
    full_path = os.path.join(_data_dir, file_path)

    # Validate all the data files in the data directory
    # against their respective schemas
    if full_path.endswith('METADATA.json'):
        return
    if full_path.endswith('REFERENCES.json'):
        validator.validate('references', full_path)
    elif full_path.endswith('.table.json'):
        validator.validate('table', full_path)
    elif full_path.endswith('.element.json'):
        validator.validate('element', full_path)
    else:
        validator.validate('component', full_path)

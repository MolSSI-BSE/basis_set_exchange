"""
Validation tests for the data
"""

import bse
import pytest
import glob
import os

data_dir = bse.default_data_dir

_all_files = glob.glob(os.path.join(data_dir, '*.json'))
_all_files.extend(glob.glob(os.path.join(data_dir, '*', '*.json')))

@pytest.mark.parametrize('file_path', _all_files)
def test_valid(file_path):
    # Validate all the data files in the data directory
    # against their respective schemas
    if file_path.endswith('METADATA.json'):
        return
    if file_path.endswith('REFERENCES.json'):
        bse.validate('references', file_path)
    elif file_path.endswith('.table.json'):
        bse.validate('table', file_path)
    elif file_path.endswith('.element.json'):
        bse.validate('element', file_path)
    else:
        bse.validate('component', file_path)

"""
Tests validation of basis set data
"""

import bz2
import os
import json
import pytest

from basis_set_exchange import validator
from .common_testvars import validator_test_data_dir

test_files = os.listdir(validator_test_data_dir)
test_files = [x for x in test_files if x.endswith('.bz2')]

@pytest.mark.parametrize('file_rel_path', test_files)
def test_validator(file_rel_path):
    file_path = os.path.join(validator_test_data_dir, file_rel_path)
    is_bad = ".bad." in os.path.basename(file_path)
    file_type = os.path.basename(file_path).split('.')[1]

    with bz2.open(file_path, 'rt', encoding='utf-8') as tf:
        file_data = tf.read()
    
    if is_bad:
        # Read the first line of the file. This will contain the string
        # that should match the exception
        file_data_lines = file_data.splitlines()
        match = file_data_lines[0][8:].strip()
        json_data = json.loads('\n'.join(file_data_lines[1:]))

        with pytest.raises(Exception, match=match):
            validator.validate_data(file_type, json_data)

    else:
        json_data = json.loads(file_data)
        validator.validate_data(file_type, json_data)

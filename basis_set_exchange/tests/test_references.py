"""
Tests for reference handling
"""

import json
import os
import pytest

from basis_set_exchange import api, validator, fileio
from .common_testvars import data_dir, all_component_files


def test_valid_reffile():
    '''
    Test to make sure the references file is valid
    '''
    full_path = os.path.join(data_dir, "REFERENCES.json")
    validator.validate_file('references', full_path)

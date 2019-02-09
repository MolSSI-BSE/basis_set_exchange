"""
Test for validating the formatting of the json files
"""

import glob
import os
import pytest

from basis_set_exchange import api, validator, fileio
from .common_testvars import all_files, data_dir


@pytest.mark.parametrize('file_path', all_files[0])
def test_valid_meta(file_path):
    full_path = os.path.join(data_dir, file_path)
    validator.validate_file('metadata', full_path)


@pytest.mark.parametrize('file_path', all_files[1])
def test_valid_table(file_path):
    full_path = os.path.join(data_dir, file_path)
    validator.validate_file('table', full_path)


@pytest.mark.parametrize('file_path', all_files[2])
def test_valid_element(file_path):
    full_path = os.path.join(data_dir, file_path)
    validator.validate_file('element', full_path)


@pytest.mark.parametrize('file_path', all_files[3])
def test_valid_component(file_path):
    full_path = os.path.join(data_dir, file_path)
    validator.validate_file('component', full_path)


def test_valid_data_dir():
    validator.validate_data_dir(data_dir)

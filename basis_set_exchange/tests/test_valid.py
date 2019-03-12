"""
Test for validating the formatting of the json files
"""

import glob
import os
import pytest

from basis_set_exchange import validator
from .common_testvars import all_metadata_paths, all_table_paths, all_element_paths, all_component_paths, data_dir


@pytest.mark.parametrize('file_path', all_metadata_paths)
def test_valid_meta(file_path):
    validator.validate_file('metadata', file_path)


@pytest.mark.parametrize('file_path', all_table_paths)
def test_valid_table(file_path):
    validator.validate_file('table', file_path)


@pytest.mark.parametrize('file_path', all_element_paths)
def test_valid_element(file_path):
    validator.validate_file('element', file_path)


@pytest.mark.parametrize('file_path', all_component_paths)
def test_valid_component(file_path):
    validator.validate_file('component', file_path)


def test_valid_reffile():
    '''
    Test to make sure the references file is valid
    '''
    file_path = os.path.join(data_dir, "REFERENCES.json")
    validator.validate_file('references', file_path)


def test_valid_data_dir():
    validator.validate_data_dir(data_dir)

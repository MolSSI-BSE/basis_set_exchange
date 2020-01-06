"""
Test for validating the formatting of the json files
"""

import os
import pytest

from basis_set_exchange import api, validator
from .common_testvars import bs_names_vers, all_metadata_paths, all_table_paths, all_element_paths, all_component_paths, data_dir


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


@pytest.mark.parametrize('bs_name,bs_ver', bs_names_vers)
def test_valid_complete(bs_name, bs_ver):
    '''Test that all basis set data is valid when obtained through get_basis'''
    data = api.get_basis(bs_name, version=bs_ver)
    validator.validate_data('complete', data)

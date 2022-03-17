# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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

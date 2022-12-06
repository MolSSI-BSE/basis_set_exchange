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
Tests BSE curation functions
"""

import os
import pytest

from basis_set_exchange import printing, fileio, api
from .common_testvars import data_dir


# yapf: disable
@pytest.mark.parametrize('basis, element', [
                              ['6-31g', '8'],
                              ['CRENBL', '3'],
                              ['CRENBL', '92'],
                              ['LANL2DZ', '78']
                         ])
# yapf: enable
def test_print_element_data(basis, element):
    eldata = api.get_basis(basis)['elements'][element]
    printing.element_data_str(element, eldata)


# yapf: disable
@pytest.mark.parametrize('file_path', [
                              'dunning/cc-pVDZ.1.json',
                              'crenb/CRENBL.0.json',
                              'crenb/CRENBL-ECP.0.json'
                         ])
# yapf: enable
def test_print_component_basis(file_path):
    full_path = os.path.join(data_dir, file_path)
    comp = fileio.read_json_basis(full_path)
    printing.component_basis_str(comp)

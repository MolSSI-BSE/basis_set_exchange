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
Validation of bibtex output
"""

import pytest
import json
from basis_set_exchange import api, lut
from .common_testvars import bs_names

_has_qcschema = True
try:
    import qcschema
except ImportError:
    _has_qcschema = False


# yapf: disable
@pytest.mark.skipif(not _has_qcschema, reason="QCSchema not available to test qcschema output")
@pytest.mark.parametrize('basis_name', bs_names)
# yapf: enable
def test_valid_qcschema_slow(basis_name):
    basis_dict = api.get_basis(basis_name)
    qcs_str = api.get_basis(basis_name, fmt='qcschema')
    qcs_json = json.loads(qcs_str)

    el_list = [lut.element_sym_from_Z(x, True) for x in basis_dict['elements'].keys()]
    coords = []
    for idx, el in enumerate(el_list):
        coords.extend((0.0, 0.0, float(idx)))

    qcs_json['atom_map'] = list(qcs_json['center_data'].keys())
    assert len(qcs_json['atom_map']) == len(el_list)

    dummy_inp = {
        "schema_name": "qc_schema_input",
        "schema_version": 1,
        "keywords": {},
        "molecule": {
            "schema_name": "qcschema_molecule",
            "schema_version": 2,
            "geometry": coords,
            "symbols": el_list
        },
        'driver': 'energy',
        'model': {
            'method': 'B3LYP',
            'basis': qcs_json
        }
    }

    qcschema.validate(dummy_inp, 'input')

"""
Validation of bibtex output
"""

import pytest
import json
from basis_set_exchange import api,lut
from .common_testvars import bs_names_sample

_has_qcschema = True
try:
    import qcschema
except:
    _has_qcschema = False

# yapf: disable
@pytest.mark.skipif(_has_qcschema is False, reason="QCSchema not available to test qcschema output")
@pytest.mark.parametrize('basis_name', bs_names_sample)
# yapf: enable
def test_valid_qcschema(basis_name):
    basis_dict = api.get_basis(basis_name)
    qcs_str = api.get_basis(basis_name, fmt='qcschema')
    qcs_json = json.loads(qcs_str)

    el_list = [lut.element_sym_from_Z(x, True) for x in basis_dict['elements'].keys()]
    coords = []
    for idx,el in enumerate(el_list):
        coords.extend((0.0, 0.0, float(idx)))

    qcs_json['basis_atom_map'] = list(qcs_json['basis_data'].keys())
    assert len(qcs_json['basis_atom_map']) == len(el_list)

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

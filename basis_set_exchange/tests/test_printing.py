"""
Tests BSE curation functions
"""

import os
import pytest
import shutil
import bz2

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

"""
Compares basis sets with authoritative versions
"""

import os

import pytest
from basis_set_exchange import misc, curate
from .common_testvars import *

# Find the dir with all the bse files
_my_dir = os.path.dirname(os.path.abspath(__file__))
_auth_data_dir = os.path.join(_my_dir, 'sources')

# create a map of the sources dir
_basis_src_map = {}
for x in os.listdir(_auth_data_dir):
    # remove .fmt.bz2
    base,_ = os.path.splitext(x)
    base,_ = os.path.splitext(base)

    if base in _basis_src_map:
        raise RuntimeError("Duplicate basis set in authoritative sources: {}".format(base))

    _basis_src_map[base] = os.path.join(_auth_data_dir, x)

@pytest.mark.parametrize('basis_name_ver', list(_basis_src_map.keys()))
def test_authoritative(basis_name_ver):
    basis_name,ver = os.path.splitext(basis_name_ver)
    ver = ver[1:] # remove starting '.'
    basis_meta = bs_metadata[basis_name]

    ref_filename = _basis_src_map[basis_name_ver]

    if not basis_name in bs_names:
        raise RuntimeError("Source basis {} doesn't have a BSE basis".format(basis_name))

    assert curate.compare_basis_against_ref(basis_name, ref_filename, version=ver, uncontract_general=True) 
            

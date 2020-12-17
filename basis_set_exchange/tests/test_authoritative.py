"""
Compares basis sets with authoritative versions
"""

import os
import pytest

from basis_set_exchange import curate
from .common_testvars import bs_metadata, bs_names, auth_src_map


@pytest.mark.parametrize("basis_name_ver", list(auth_src_map.keys()))
def test_authoritative(basis_name_ver):
    """
    Compare the stored basis sets with the stored authoritative sources
    """

    basis_name, ver = os.path.splitext(basis_name_ver)
    ver = ver[1:]  # remove starting '.'

    basis_meta = bs_metadata[basis_name]

    ref_path = auth_src_map[basis_name_ver]

    if basis_name not in bs_names:
        raise RuntimeError(
            "Source basis {} doesn't have a BSE basis".format(basis_name)
        )

    assert curate.compare_basis_against_file(
        basis_name, ref_path, version=ver, uncontract_general=True
    )

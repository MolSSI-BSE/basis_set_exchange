"""
Tests BSE curation functions
"""

import os
import tempfile

import pytest
from basis_set_exchange import api, curate, manip
from .common_testvars import bs_names_sample

roundtrip_formats = ['turbomole', 'gaussian94', 'nwchem']


@pytest.mark.parametrize('basis', bs_names_sample)
@pytest.mark.parametrize('fmt', roundtrip_formats)
def test_curate_roundtrip(basis, fmt):

    # Many formats have limitations on general contractions
    if fmt == 'gaussian94':
        uncontract_general = True
        uncontract_spdf = 1
    if fmt == 'turbomole':
        uncontract_general = True
        uncontract_spdf = 0
    if fmt == 'nwchem':
        uncontract_general = False
        uncontract_spdf = 1

    bse_formatted = api.get_basis(basis, fmt=fmt)
    bse_dict = api.get_basis(basis, uncontract_general=uncontract_general)
    bse_dict = manip.uncontract_spdf(bse_dict, uncontract_spdf)

    outfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
    outfile_path = outfile.name
    outfile.write(bse_formatted)
    outfile.close()

    test_dict = curate.read_formatted_basis(outfile_path, fmt)
    os.remove(outfile_path)

    test_dict = manip.sort_basis(test_dict)
    bse_dict = manip.sort_basis(bse_dict)

    # Compare, ignoring metadata (not stored in most formats)
    assert curate.compare_basis(bse_dict, test_dict, rel_tol=0.0)

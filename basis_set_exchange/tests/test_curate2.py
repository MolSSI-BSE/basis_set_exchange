"""
Tests BSE curation functions
"""

import os
import tempfile
import pytest

from basis_set_exchange import curate, api, manip, validator
from .common_testvars import auth_data_dir


@pytest.mark.parametrize('refs', [None, 'madeup_ref'])
def test_add_basis(tmp_path, refs):
    tmp_path = str(tmp_path)  # Needed for python 3.5
    source_files = ['cc-pvdz.1.gbasis.bz2', 'def2-tzvp.1.tm.bz2', 'def2-ecp.1.tm.bz2']
    for sf in source_files:
        sf_path = os.path.join(auth_data_dir, sf)

        name = sf.split('.')[0]
        curate.add_basis(sf_path, tmp_path, 'test_subdir', 'test_' + name, 'test_basis_' + name, 'test_family',
                         'orbital', 'Test Basis Description: ' + name, '1', 'Test Basis Revision Description', refs)

    md = api.get_metadata(tmp_path)
    assert len(md) == len(source_files)

    # Re-read
    for sf in source_files:
        name = name = sf.split('.')[0]
        name = 'test_basis_' + name
        bse_dict = api.get_basis(name, data_dir=tmp_path)

        assert bse_dict['basis_set_family'] == 'test_family'

        # Compare against the file we created from
        sf_path = os.path.join(auth_data_dir, sf)
        test_dict = curate.read_formatted_basis(sf_path)

        # Compare, ignoring metadata (not stored in most formats)
        assert curate.compare_basis(bse_dict, test_dict, rel_tol=0.0)

    # Validate the new data dir
    validator.validate_data_dir(tmp_path)

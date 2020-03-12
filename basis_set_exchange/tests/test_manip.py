"""
Tests BSE manip functions
"""

import os
import pytest

from basis_set_exchange import api, curate, manip, readers
from .common_testvars import bs_names_sample, dunningext_test_data_dir

dunningext_test_subdirs = os.listdir(dunningext_test_data_dir)
dunningext_test_subdirs = [x for x in dunningext_test_subdirs if x.startswith('aug-')]


@pytest.mark.parametrize('basis', bs_names_sample)
def test_manip_roundtrip(basis):
    bse_dict = api.get_basis(basis, uncontract_general=True, uncontract_spdf=True)
    bse_dict_gen = manip.make_general(bse_dict)
    bse_dict_unc = manip.uncontract_general(bse_dict_gen)

    assert curate.compare_basis(bse_dict, bse_dict_unc, rel_tol=0.0)


@pytest.mark.parametrize('testdir', dunningext_test_subdirs)
def test_manip_dunningext(testdir):
    full_testdir = os.path.join(dunningext_test_data_dir, testdir)
    basefile = testdir + '.nw.bz2'
    base_data = readers.read_formatted_basis_file(os.path.join(full_testdir, basefile))

    for level, prefix in [(2, 'd-'), (3, 't-'), (4, 'q-')]:
        ref = prefix + testdir + '.nw.ref.bz2'
        full_ref_path = os.path.join(full_testdir, ref)
        ref_data = readers.read_formatted_basis_file(full_ref_path, 'nwchem')
        ref_data = manip.make_general(ref_data)

        new_data = manip.extend_dunning_aug(base_data, level)
        new_data = manip.make_general(new_data)
        assert curate.compare_basis(new_data, ref_data)

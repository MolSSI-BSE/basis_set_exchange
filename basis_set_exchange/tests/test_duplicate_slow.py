'''
Test for duplicate data in a basis set
'''

import os
import pytest
import basis_set_exchange as bse
from basis_set_exchange import curate
from .common_testvars import bs_names_vers, test_data_dir, true_false
from .test_duplicate import _test_duplicates


@pytest.mark.slow
@pytest.mark.parametrize('bs_name,bs_ver', bs_names_vers)
@pytest.mark.parametrize('unc_gen', true_false)
@pytest.mark.parametrize('unc_seg', true_false)
@pytest.mark.parametrize('unc_spdf', true_false)
@pytest.mark.parametrize('make_gen', true_false)
@pytest.mark.parametrize('opt_gen', true_false)
def test_duplicate_slow(bs_name, bs_ver, unc_gen, unc_seg, unc_spdf, opt_gen, make_gen):
    '''
    Test for any duplicate data in a basis set
    '''

    bs_dict = bse.get_basis(bs_name, version=bs_ver,
                            uncontract_general=unc_gen,
                            uncontract_segmented=unc_seg,
                            uncontract_spdf=unc_spdf,
                            make_general=make_gen,
                            optimize_general=opt_gen)

    _test_duplicates(bs_dict, False)

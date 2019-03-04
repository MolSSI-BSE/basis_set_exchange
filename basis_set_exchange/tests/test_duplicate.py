'''
Test for duplicate data in a basis set
'''

import os
import pytest
import basis_set_exchange as bse
from basis_set_exchange import curate
from .common_testvars import bs_names_vers, test_data_dir, true_false


def _test_duplicates(bs_dict):
    '''
    Test for any duplicate data in a basis set
    '''

    found_dupe = False
    for el, eldata in bs_dict['basis_set_elements'].items():
        if 'element_electron_shells' in eldata:
            # Quick and dirty
            shells = eldata['element_electron_shells']

            for sh in shells:
                if shells.count(sh) != 1:
                    print("Shell Dupe: element {}".format(el))
                    found_dupe = True
                    break

        if 'element_ecp' in eldata:
            pots = eldata['element_ecp']

            for pot in pots:
                if pots.count(pot) != 1:
                    print("ECP Dupe: element {}".format(el))
                    found_dupe = True
                    break

    assert found_dupe == False


@pytest.mark.parametrize('bs_name,bs_ver', bs_names_vers)
def test_duplicate_data(bs_name, bs_ver):
    '''
    Test for any duplicate data in a basis set
    '''

    bs_dict = bse.get_basis(bs_name, version=bs_ver)

    _test_duplicates(bs_dict)


@pytest.mark.xfail
@pytest.mark.parametrize('filename', ['6-31g-bse-DUPE.nw.bz2', 'def2-ecp-DUPE.nw.bz2'])
def test_duplicate_fail(filename):
    filepath = os.path.join(test_data_dir, filename)

    filedata = curate.read_formatted_basis(filepath, 'nwchem')
    _test_duplicates(filedata)


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

    _test_duplicates(bs_dict)

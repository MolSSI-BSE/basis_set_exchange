'''
Test for duplicate data in a basis set
'''

import os
import pytest
import basis_set_exchange as bse
from basis_set_exchange import curate
from .common_testvars import bs_names_vers, test_data_dir, true_false


def _test_duplicates(bs_dict, expected):
    '''
    Test for any duplicate data in a basis set
    '''

    found_dupe = False
    for el, eldata in bs_dict['elements'].items():
        if 'electron_shells' in eldata:
            # Quick and dirty
            shells = eldata['electron_shells']

            for sh in shells:
                if shells.count(sh) != 1:
                    print("Shell Dupe: element {}".format(el))
                    found_dupe = True
                    break

        if 'ecp_potentials' in eldata:
            pots = eldata['ecp_potentials']

            for pot in pots:
                if pots.count(pot) != 1:
                    print("ECP Dupe: element {}".format(el))
                    found_dupe = True
                    break

    assert found_dupe == expected


@pytest.mark.parametrize('bs_name,bs_ver', bs_names_vers)
def test_duplicate_data(bs_name, bs_ver):
    '''
    Test for any duplicate data in a basis set
    '''

    bs_dict = bse.get_basis(bs_name, version=bs_ver)
    _test_duplicates(bs_dict, False)


@pytest.mark.parametrize('filename', ['6-31g-bse-DUPE.nw.bz2', 'def2-ecp-DUPE.nw.bz2'])
def test_duplicate_fail(filename):
    filepath = os.path.join(test_data_dir, filename)
    filedata = curate.read_formatted_basis(filepath, 'nwchem')
    _test_duplicates(filedata, True)

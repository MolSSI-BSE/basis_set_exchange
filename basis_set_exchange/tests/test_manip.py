"""
Tests BSE manip functions
"""

import os
import pytest

from basis_set_exchange import api, curate, manip, readers
from .common_testvars import bs_names_sample, dunningext_test_data_dir, truhlar_test_data_dir, rmfree_test_data_dir

def _list_subdirs(path):
    """
    Create a list of subdirectories of a path.

    The returned paths will be relative to the given path.
    """

    subdirs = [os.path.join(path, x) for x in os.listdir(path)]
    return [os.path.relpath(x, path) for x in subdirs if os.path.isdir(x)]

dunningext_test_subdirs = _list_subdirs(dunningext_test_data_dir)
truhlar_test_subdirs = _list_subdirs(truhlar_test_data_dir)
rmfree_test_subdirs = _list_subdirs(rmfree_test_data_dir)


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


@pytest.mark.parametrize('testdir', truhlar_test_subdirs)
def test_manip_truhlar(testdir):
    full_testdir = os.path.join(truhlar_test_data_dir, testdir)
    basefile = 'aug-' + testdir + '.nw.bz2'
    base_data = readers.read_formatted_basis_file(os.path.join(full_testdir, basefile))

    ref_files = os.listdir(full_testdir)
    ref_files = [x for x in ref_files if x.endswith('.ref.bz2')]

    # Made a mistake here once where reference files weren't being read
    assert ref_files

    for ref in ref_files:
        month = ref.split('-')[0]
        full_ref_path = os.path.join(full_testdir, ref)
        ref_data = readers.read_formatted_basis_file(full_ref_path, 'nwchem')
        ref_data = manip.make_general(ref_data)

        new_data = manip.truhlar_calendarize(base_data, month, use_copy=True)
        assert curate.compare_basis(new_data, ref_data)


@pytest.mark.parametrize('testdir', rmfree_test_subdirs)
def test_manip_remove_free(testdir):
    full_testdir = os.path.join(rmfree_test_data_dir, testdir)
    basefile = testdir + '.nw.bz2'
    base_data = readers.read_formatted_basis_file(os.path.join(full_testdir, basefile))

    ref = 'min_' + testdir + '.nw.ref.bz2'
    full_ref_path = os.path.join(full_testdir, ref)
    ref_data = readers.read_formatted_basis_file(full_ref_path, 'nwchem')
    ref_data = manip.make_general(ref_data)

    new_data = manip.remove_free_primitives(base_data)
    new_data = manip.make_general(new_data)
    assert curate.compare_basis(new_data, ref_data)


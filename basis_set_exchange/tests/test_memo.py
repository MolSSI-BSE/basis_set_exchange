"""
Tests of memoization
"""

import random
import pytest
import time
import basis_set_exchange as bse

from .common_testvars import *

# Use random for getting sets of elements
random.seed(rand_seed, version=2)


def _test_memo_helper(func, *args, **kwargs):
    start = time.time()
    try1 = func(*args, **kwargs)
    mid = time.time()
    try2 = func(*args, **kwargs)
    end = time.time()

    # Time should be shorter, but is a bit
    # non-determinstic
    #print(end-mid, mid-start)
    #assert (end-mid) < (mid-start)

    # Should be equal, but not aliased
    assert try1 == try2

    # Empty strings are the same
    if try1 == '':
        return

    assert try1 is not try2


def test_get_metadata_memo():
    """Test memoization of get_metadata"""
    _test_memo_helper(bse.get_metadata)


def test_get_reference_data_memo():
    """Test memoization of get_reference_data"""
    _test_memo_helper(bse.get_reference_data)


@pytest.mark.parametrize('basis_name', bs_names_sample)
def test_get_basis_notes_memo(basis_name):
    """Test memoization of get_basis_notes"""
    _test_memo_helper(bse.get_basis_notes, basis_name)


@pytest.mark.parametrize('basis_name', bs_names_sample)
def test_get_basis_memo(basis_name):
    """Test memoization of get_basis_notes"""
    _test_memo_helper(bse.get_basis, basis_name)


@pytest.mark.parametrize('family', all_families)
def test_get_family_notes_memo(family):
    """Test memoization of get_family_notes"""
    _test_memo_helper(bse.get_family_notes, family)

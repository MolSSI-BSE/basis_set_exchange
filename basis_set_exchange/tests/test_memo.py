# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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
    # non-deterministic
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

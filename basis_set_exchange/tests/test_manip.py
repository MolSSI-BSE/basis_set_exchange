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
Tests BSE's manipulation functions (manip)
"""

import os
import copy
import pytest

from basis_set_exchange import api, curate, manip, readers, sort
from .common_testvars import bs_names_sample, diffuse_augmentation_test_data_dir, steep_augmentation_test_data_dir, truhlar_test_data_dir, rmfree_test_data_dir


def _list_subdirs(path):
    """
    Create a list of subdirectories of a path.

    The returned paths will be relative to the given path.
    """

    subdirs = [os.path.join(path, x) for x in os.listdir(path)]
    return [os.path.relpath(x, path) for x in subdirs if os.path.isdir(x)]


diffuse_augmentation_test_subdirs = _list_subdirs(diffuse_augmentation_test_data_dir)
steep_augmentation_test_subdirs = _list_subdirs(steep_augmentation_test_data_dir)
truhlar_test_subdirs = _list_subdirs(truhlar_test_data_dir)
rmfree_test_subdirs = _list_subdirs(rmfree_test_data_dir)


@pytest.mark.parametrize('basis', bs_names_sample)
def test_manip_roundtrip(basis):
    bse_dict = api.get_basis(basis, uncontract_general=True, uncontract_spdf=True)
    bse_dict_gen = manip.make_general(bse_dict)
    bse_dict_unc = manip.uncontract_general(bse_dict_gen)

    assert curate.compare_basis(bse_dict, bse_dict_unc, rel_tol=0.0)


@pytest.mark.parametrize('testdir', diffuse_augmentation_test_subdirs)
def test_manip_diffuse_augmentation(testdir):
    full_testdir = os.path.join(diffuse_augmentation_test_data_dir, testdir)
    basefile = testdir + '.nw.bz2'
    base_data = readers.read_formatted_basis_file(os.path.join(full_testdir, basefile))

    for level, prefix in [(1, 'd'), (2, 't'), (3, 'q')]:
        ref = prefix + testdir + '.nw.ref.bz2'
        full_ref_path = os.path.join(full_testdir, ref)
        ref_data = readers.read_formatted_basis_file(full_ref_path, 'nwchem')
        ref_data = manip.make_general(ref_data)

        new_data = manip.geometric_augmentation(base_data, level, steep=False)
        new_data = manip.make_general(new_data)
        assert curate.compare_basis(new_data, ref_data)


@pytest.mark.parametrize('testdir', steep_augmentation_test_subdirs)
def test_manip_steep_augmentation(testdir):
    full_testdir = os.path.join(steep_augmentation_test_data_dir, testdir)
    basefile = testdir + '.nw.bz2'
    base_data = readers.read_formatted_basis_file(os.path.join(full_testdir, basefile))

    for slevel, sprefix in [(0, ''), (1, 's'), (2, 'd')]:
        # diffuse level 0 is augmented, 1 is doubly augmented
        for dlevel, dprefix in [(0, ''), (1, 'd'), (2, 't')]:
            if slevel == 0 and dlevel == 0:
                continue
            ref = testdir.replace('un-', 'un{}-'.format(sprefix)).replace('aug-',
                                                                          '{}aug-'.format(dprefix)) + '.nw.ref.bz2'
            full_ref_path = os.path.join(full_testdir, ref)
            ref_data = readers.read_formatted_basis_file(full_ref_path, 'nwchem')
            ref_data = manip.make_general(ref_data)

            new_data = copy.deepcopy(base_data)
            if slevel > 0:
                new_data = manip.geometric_augmentation(new_data, slevel, steep=True)
            if dlevel > 0:
                new_data = manip.geometric_augmentation(new_data, dlevel, steep=False)
            # The basis has to be sorted, since this also happens in the writers
            new_data = sort.sort_basis(new_data)
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

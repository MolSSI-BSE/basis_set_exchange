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
Tests for creating bundles/archives of formatted data
"""

import os
import sys
import zipfile
import tarfile
import pytest

import basis_set_exchange as bse
from .common_testvars import fake_data_dir

_bundle_types = bse.bundle.get_archive_types()
_bundle_exts = [v['extension'] for v in _bundle_types.values()]


def _extract_all(filepath, extract_dir):
    if filepath.endswith('.zip'):
        with zipfile.ZipFile(filepath, 'r') as zf:
            zf.extractall(extract_dir)
    elif filepath.endswith('.tar.bz2'):
        with tarfile.open(filepath, 'r:bz2') as tf:
            if sys.version_info >= (3, 11):
                tf.extractall(extract_dir, filter='fully_trusted')
            else:
                tf.extractall(extract_dir)
    else:
        raise RuntimeError("Unexpected file extension")


def _run_test_bundles(tmp_path, fmt, reffmt, ext, data_dir):
    '''Test functionality related to creating archive of basis set'''

    tmp_path = str(tmp_path)  # Needed for python 3.5

    bs_ext = bse.writers.get_format_extension(fmt)
    ref_ext = bse.refconverters.get_format_extension(reffmt)

    filename = "bundletest_" + fmt + "_" + reffmt + ext
    filepath = os.path.join(tmp_path, filename)

    bse.create_bundle(filepath, fmt, reffmt, None, data_dir)
    extract_dir = "extract_" + filename
    extract_path = os.path.join(tmp_path, extract_dir)
    _extract_all(filepath, extract_path)

    # Keep track of all the basis sets we have found
    # Start with all found in the data dir, and remove
    # each time we process one
    all_bs = []
    for k, v in bse.get_metadata(data_dir).items():
        for ver in v['versions'].keys():
            all_bs.append((k, ver))

    all_ref = all_bs.copy()

    for root, dirs, files in os.walk(extract_path):
        for basename in files:
            if basename == 'README.txt':
                continue

            fpath = os.path.join(root, basename)
            name, ver = basename.split('.')[:2]
            tr_name = bse.misc.basis_name_from_filename(name)

            if basename.endswith('.ref' + ref_ext):
                compare_data = bse.get_references(tr_name, fmt=reffmt, version=ver, data_dir=data_dir)
                all_ref.remove((name, ver))
            elif basename.endswith(bs_ext):
                compare_data = bse.get_basis(name, fmt=fmt, version=ver, data_dir=data_dir)
                all_bs.remove((name, ver))
            elif basename.endswith('.family_notes'):
                compare_data = bse.get_family_notes(name, data_dir)
            elif basename.endswith('.notes'):
                compare_data = bse.get_basis_notes(name, data_dir)
            else:
                raise RuntimeError("Unknown file found: " + fpath)

            with open(fpath, 'r', encoding='utf-8') as ftmp:
                assert compare_data == ftmp.read()

    assert len(all_bs) == 0
    assert len(all_ref) == 0


# yapf: disable
@pytest.mark.parametrize('ext', _bundle_exts)
@pytest.mark.parametrize('fmt, reffmt', [('nwchem', 'bib'),
                                         ('psi4', 'txt')])
# yapf: enable
def test_bundles_fast(tmp_path, fmt, reffmt, ext):
    _run_test_bundles(tmp_path, fmt, reffmt, ext, fake_data_dir)

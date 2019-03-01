"""
Tests for creating bundles/archives of formatted data
"""

import os
import zipfile
import tarfile
import pytest
import shutil
import glob

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
            tf.extractall(extract_dir)
    else:
        raise RuntimeError("Unexpected file extension")


# yapf: disable
@pytest.mark.slow
@pytest.mark.parametrize('ext', _bundle_exts)
@pytest.mark.parametrize('fmt, reffmt', [('nwchem', 'bib'),
                                         ('psi4', 'txt')])
# yapf: enable
def _run_test_bundles(tmp_path, fmt, reffmt, ext, data_dir):
    '''Test functionality related to creating archive of basis set'''

    tmp_path = str(tmp_path)  # Needed for python 3.5

    bs_ext = bse.converters.get_format_extension(fmt)
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
    all_bs_names = bse.get_all_basis_names(data_dir)
    all_ref_names = all_bs_names.copy()

    for root, dirs, files in os.walk(extract_path):
        for basename in files:
            fpath = os.path.join(root, basename)
            name = basename.split('.')[0]
            if basename.endswith('.ref' + ref_ext):
                compare_data = bse.get_references(name, fmt=reffmt, data_dir=data_dir)
                all_bs_names.remove(name)
            elif basename.endswith(bs_ext):
                compare_data = bse.get_basis(name, fmt=fmt, data_dir=data_dir)
                all_ref_names.remove(name)
            elif basename.endswith('.family_notes'):
                compare_data = bse.get_family_notes(name, data_dir)
            elif basename.endswith('.notes'):
                compare_data = bse.get_basis_notes(name, data_dir)
            else:
                raise RuntimeError("Unknown file found: " + fpath)

            with open(fpath, 'r') as ftmp:
                assert compare_data == ftmp.read()

    assert len(all_bs_names) == 0
    assert len(all_ref_names) == 0


# yapf: disable
@pytest.mark.parametrize('ext', _bundle_exts)
@pytest.mark.parametrize('fmt, reffmt', [('nwchem', 'bib'),
                                         ('psi4', 'txt')])
# yapf: enable
def test_bundles_fast(tmp_path, fmt, reffmt, ext):
   _run_test_bundles(tmp_path, fmt, reffmt, ext, fake_data_dir)


# yapf: disable
@pytest.mark.slow
@pytest.mark.parametrize('ext', _bundle_exts)
@pytest.mark.parametrize('fmt, reffmt', [('nwchem', 'bib'),
                                         ('psi4', 'txt')])
# yapf: enable
def test_bundles_slow(tmp_path, fmt, reffmt, ext):
   _run_test_bundles(tmp_path, fmt, reffmt, ext, None)
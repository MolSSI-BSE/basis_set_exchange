"""
Tests for creating bundles/archives of formatted data
"""

import os
import tempfile
import filecmp
import zipfile
import tarfile
import pytest
import shutil
import glob

from basis_set_exchange import bundle, converters, refconverters
from .common_testvars import bs_names


def _extract_file(filepath, extract_dir):
    if filepath.endswith('.zip'):
        with zipfile.ZipFile(filepath, 'r') as zf:
            zf.extractall(extract_dir)
    elif filepath.endswith('.tar.bz2'):
        with tarfile.open(filepath, 'r:bz2') as tf:
            tf.extractall(extract_dir)
    else:
        raise RuntimeError("Unexpected file extension")


# yapf: disable
@pytest.mark.parametrize('fmt, reffmt', [('nwchem', 'bib'),
                                         ('psi4', 'txt')])
# yapf: enable
def test_bundles(fmt, reffmt):
    '''Test functionality related to creating archive of basis set'''

    exts = ['.zip', '.tar.bz2']

    bs_ext = converters.get_format_extension(fmt)
    ref_ext = refconverters.get_format_extension(reffmt)
    nbasis = len(bs_names)

    tdir = tempfile.mkdtemp()

    ex_dirs = []
    for ext in exts:
        filename = "bundletest_" + fmt + "_" + reffmt + ext
        filepath = os.path.join(tdir, filename)

        bundle.create_bundle(filepath, fmt, reffmt)
        extract_dir = "extract_" + filename
        extract_path = os.path.join(tdir, extract_dir)
        _extract_file(filepath, extract_path)

        ex_dirs.append(extract_path)

    # Check that one file exists per basis
    for d in ex_dirs:
        bs_flist = glob.glob(os.path.join(d, '*' + bs_ext))
        bs_flist = [x for x in bs_flist if not '.ref.' in x]
        ref_flist = glob.glob(os.path.join(d, '*.ref' + ref_ext))
        assert len(bs_flist) == nbasis
        assert len(ref_flist) == nbasis

    # Compare file contents across archive types
    for d in ex_dirs[1:]:
        compare = filecmp.dircmp(d, ex_dirs[0])
        assert len(compare.diff_files) == 0
        assert len(compare.left_only) == 0
        assert len(compare.right_only) == 0

    shutil.rmtree(tdir)

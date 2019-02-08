"""
Tests for creating bundles/archives of formatted data
"""

import os
import tempfile
import zipfile
import tarfile
import pytest
import shutil
import glob

from basis_set_exchange import bundle, converters, refconverters, get_basis, get_references
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
@pytest.mark.parametrize('ext', ['.zip', '.tar.bz2'])
@pytest.mark.parametrize('fmt, reffmt', [('nwchem', 'bib'),
                                         ('psi4', 'txt')])
# yapf: enable
def test_bundles(fmt, reffmt, ext):
    '''Test functionality related to creating archive of basis set'''

    exts = ['.zip', '.tar.bz2']

    bs_ext = converters.get_format_extension(fmt)
    ref_ext = refconverters.get_format_extension(reffmt)
    nbasis = len(bs_names)

    tdir = tempfile.mkdtemp()

    filename = "bundletest_" + fmt + "_" + reffmt + ext
    filepath = os.path.join(tdir, filename)

    bundle.create_bundle(filepath, fmt, reffmt)
    extract_dir = "extract_" + filename
    extract_path = os.path.join(tdir, extract_dir)
    _extract_file(filepath, extract_path)

    bs_flist = glob.glob(os.path.join(extract_path, '*' + bs_ext))
    bs_flist = [x for x in bs_flist if not '.ref.' in x]
    ref_flist = glob.glob(os.path.join(extract_path, '*.ref' + ref_ext))

    for bs in bs_flist:
        bs_name = os.path.basename(bs)
        bs_name = os.path.splitext(bs_name)[0]
        bs_str = get_basis(bs_name, fmt=fmt)

        with open(bs, 'r') as bsf:
            assert bs_str == bsf.read()

    for ref in ref_flist:
        bs_name = os.path.basename(ref)
        bs_name = os.path.splitext(bs_name)[0]
        bs_name = os.path.splitext(bs_name)[0]  # remove .ref.
        ref_str = get_references(bs_name, fmt=reffmt)

        with open(ref, 'r') as rf:
            assert ref_str == rf.read()

    shutil.rmtree(tdir)

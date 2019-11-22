"""
Tests for creating bundles/archives of formatted data
"""

import pytest

from .test_bundle import _run_test_bundles, _bundle_exts

# yapf: disable
@pytest.mark.slow
@pytest.mark.parametrize('ext', _bundle_exts)
@pytest.mark.parametrize('fmt, reffmt', [('nwchem', 'bib'),
                                         ('psi4', 'txt'),
                                         ('json', 'json')])
# yapf: enable
def test_bundles_slow(tmp_path, fmt, reffmt, ext):
    _run_test_bundles(tmp_path, fmt, reffmt, ext, None)

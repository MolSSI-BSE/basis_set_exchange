"""
Tests for BSE metadata
"""

import tempfile
import os
import pytest

from basis_set_exchange import bundle

# yapf: disable
@pytest.mark.parametrize('ext', ['.zip', '.tar.bz2'])
@pytest.mark.parametrize('fmt, reffmt', [('nwchem', 'bib'),
                                         ('psi4', 'txt')])
# yapf: enable
def test_bundles(ext, fmt, reffmt):
    '''Test functionality related to creating archive of basis set'''

    bfile_tmp = tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False)
    bfile_name = bfile_tmp.name

    bundle.create_bundle(bfile_name, fmt, reffmt)
    
    os.remove(bfile_name)

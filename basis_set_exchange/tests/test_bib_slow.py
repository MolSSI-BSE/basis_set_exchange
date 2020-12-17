"""
Validation of bibtex output
"""

import pytest
from basis_set_exchange import api

from . import check_bibtex
from .common_testvars import bs_names


# yapf: disable
@pytest.mark.slow
@pytest.mark.skipif(not check_bibtex.available, reason="Latex/Bibtex commands not found, so I can't verify bib files")
@pytest.mark.parametrize('basis_name', bs_names)
# yapf: enable
def test_bibtex(tmp_path, basis_name):
    tmp_path = str(tmp_path)  # Needed for python 3.5
    bib_str = api.get_references(basis_name, fmt="bib")
    check_bibtex.validate_bibtex(tmp_path, bib_str)

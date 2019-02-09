"""
Validation of bibtex output
"""

import pytest
from basis_set_exchange import api

from . import check_bibtex

# Load all the metadata once
_bs_names = api.get_all_basis_names()


# yapf: disable
@pytest.mark.slow
@pytest.mark.skipif(check_bibtex.available is False, reason="Latex/Bibtex commands not found, so I can't verify bib files")
@pytest.mark.parametrize('basis_name', _bs_names)
# yapf: enable
def test_bibtex(tmp_path, basis_name):
    tmp_path = str(tmp_path)  # Needed for python 3.5
    bib_str = api.get_references(basis_name, fmt='bib')
    check_bibtex.validate_bibtex(tmp_path, bib_str)

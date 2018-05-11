"""
Validation of bibtex output
"""

import bse
import pytest
from . import check_bibtex


# Load all the metadata once
_bs_names = bse.get_all_basis_names()

@pytest.mark.skipif(check_bibtex.available == False, reason="Latex/Bibtex commands not found, so I can't verify bib files")
@pytest.mark.parametrize('basis_name', _bs_names)
def test_bibtex(basis_name):
    # TODO - test getting subsets of elements
    bib_str = bse.get_references(basis_name, elements=None, fmt='bib')
    check_bibtex.validate_bibtex(bib_str)

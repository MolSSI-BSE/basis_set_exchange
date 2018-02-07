"""
Tests for reference handling
"""

from bse import refconverters
import pytest

@pytest.mark.parametrize("elements, expected", 
                         [ ([1], "H"),
                           ([1,2], "H,He"),
                           ([1,10], "H,Ne"),
                           ([1,2,3,11,23,24], "H-Li,Na,V,Cr")])
def test_compact_string(elements, expected):
    assert refconverters.compact_elements(elements) == expected

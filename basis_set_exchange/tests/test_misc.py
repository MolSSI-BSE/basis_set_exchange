"""
Tests of BSE miscellaneous functions
"""

import pytest
from basis_set_exchange import misc


# yapf: disable
@pytest.mark.parametrize("elements, expected", [([1], "H"),
                                                ([1, 2], "H,He"),
                                                ([1, 10], "H,Ne"),
                                                ([1, 2, 3, 11, 23, 24], "H-Li,Na,V,Cr")])
# yapf: enable
def test_compact_string(elements, expected):
    '''Test compacting a string of elements (and then expanding them)'''
    compacted = misc.compact_elements(elements)
    assert compacted == expected

    expanded = misc.expand_elements(compacted)
    assert expanded == elements

    expanded = misc.expand_elements(compacted, True)
    assert expanded == [str(x) for x in elements]

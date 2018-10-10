import pytest
from basis_set_exchange import misc

@pytest.mark.parametrize("elements, expected", 
                         [ ([1], "H"),
                           ([1,2], "H,He"),
                           ([1,10], "H,Ne"),
                           ([1,2,3,11,23,24], "H-Li,Na,V,Cr")])
def test_compact_string(elements, expected):
    compacted = misc.compact_elements(elements)
    assert compacted == expected

    expanded = misc.expand_elements(compacted)
    assert expanded == elements

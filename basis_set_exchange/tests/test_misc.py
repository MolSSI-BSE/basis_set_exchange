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
    """Test compacting a string of elements (and then expanding them)"""
    compacted = misc.compact_elements(elements)
    assert compacted == expected

    expanded = misc.expand_elements(compacted)
    assert expanded == elements

    expanded = misc.expand_elements(compacted, True)
    assert expanded == [str(x) for x in elements]


# yapf: disable
@pytest.mark.parametrize("compact_el, expected",
                               [("H-Li,C-O,Ne", [1, 2, 3, 6, 7, 8, 10]),
                                ("H-N,8,Na-12", [1, 2, 3, 4, 5, 6, 7, 8, 11, 12]),
                                (['C', 'Al-15,S', 17, '18'], [6, 13, 14, 15, 16, 17, 18]),
                                ([], []),
                                ([''], []),
                                (['','',''], []),
                                ('', []),
                                ('C', [6]),
                                (' 6 ', [6]),
                                (6, [6]),
                                (['6,,7', '  10  '], [6,7,10]),
                                (['6----8'], [6,7,8]),
                                ([',,,'], []),
                                ([',6,', ',Ne,,,', ',,11-Si,,'], [6,10,11,12,13,14]),
                                ('6----8', [6,7,8])])
# yapf: enable
def test_expand_elements(compact_el, expected):
    expanded = misc.expand_elements(compact_el)
    assert expanded == expected


# yapf: disable
@pytest.mark.parametrize("compact_el",
                               ['H-Li-C',
                                ['H-Li-C'],
                                '-H',
                                'H-',
                                '1-',
                                '-1',
                                '1,2-,10',
                                '1,-2,10',
                                ['1', '-2', '10']])
# yapf: enable
def test_expand_elements_fail(compact_el):
    with pytest.raises(RuntimeError, match=r"Malformed element string"):
        misc.expand_elements(compact_el)


# yapf: disable
@pytest.mark.parametrize("name,expected",
                              [('6-31g', '6-31g'),
                               ('6-31G', '6-31g'),
                               ('6-31G**', '6-31g_st__st_'),
                               ('6-31++G', '6-31++g'),
                               ('6-31++G**', '6-31++g_st__st_')])
# yapf: enable
def test_basis_name_to_filename(name, expected):
    fname = misc.basis_name_to_filename(name)
    assert fname == expected
    name2 = misc.basis_name_from_filename(fname)
    assert name2 == name.lower()

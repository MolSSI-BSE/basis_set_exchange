'''
Miscellaneous helper functions
'''

from . import lut


def compact_elements(elements):
    """
    Create a string (with ranges) given a list of element numbers

    For example, [1, 2, 3, 6, 7, 8, 10] will return "H-Li,C-O,Ne"
   """

    if len(elements) == 0:
        return

    # We have to convert to integers for this function
    elements = [int(el) for el in elements]

    # Just to be safe, sort the list
    el = sorted(set(elements))

    ranges = []
    i = 0
    while i < len(el):
        start_el = el[i]
        end_el = start_el

        i += 1
        while i < len(el):
            if el[i] != end_el + 1:
                break

            end_el += 1
            i += 1

        if start_el == end_el:
            ranges.append([start_el])
        else:
            ranges.append([start_el, end_el])

    # Convert to elemental symbols
    range_strs = []
    for r in ranges:
        sym = lut.element_sym_from_Z(r[0], True)

        if len(r) == 1:
            range_strs.append(sym)
        elif len(r) == 2 and r[1] == r[0] + 1:
            sym2 = lut.element_sym_from_Z(r[1], True)
            range_strs.append(sym + "," + sym2)
        else:
            sym2 = lut.element_sym_from_Z(r[1], True)
            range_strs.append(sym + "-" + sym2)

    return ",".join(range_strs)


def expand_elements(compact_str):
    """
    Create a list of integers given a string of compacted elements

    This is the opposite of compact_elements

    For example, "H-Li,C-O,Ne" will return [1, 2, 3, 6, 7, 8, 10]
    """

    if len(compact_str) == 0:
        return

    # Split on commas
    tmp_list = compact_str.split(',')

    # Now go over each one and replace elements with ints
    el_list = []
    for el in tmp_list:
        if not '-' in el:
            el_list.append(lut.element_Z_from_sym(el))
        else:
            begin, end = el.split('-')
            begin = lut.element_Z_from_sym(begin)
            end = lut.element_Z_from_sym(end)
            el_list.extend(list(range(int(begin), int(end) + 1)))

    return el_list


def transform_basis_name(name):
    """
    Transforms the name of a basis set to an internal representation

    This makes comparison of basis set names easier by, for example,
    converting the name to all lower case.
    """

    return name.lower()

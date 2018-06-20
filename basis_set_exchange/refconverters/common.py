'''
Helper functions for writing out references/citations in various formats
'''

from .. import lut


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

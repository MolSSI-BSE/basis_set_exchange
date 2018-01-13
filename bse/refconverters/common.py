from .. import lut

def compact_elements(elements):

    if len(elements) == 0:
        return

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
        sym = lut.element_sym_from_Z(r[0])
        sym = lut.normalize_element_symbol(sym)

        if len(r) == 1:
            range_strs.append(sym)
        else:
            sym2 = lut.element_sym_from_Z(r[1])
            sym2 = lut.normalize_element_symbol(sym2)
            range_strs.append(sym + "-" + sym2)

    return ",".join(range_strs)

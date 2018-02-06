"""
Functions related to handling of references/citations
"""

from . import io


def compact_references(basis_dict, reffile_path):
    ref_data = io.read_references(reffile_path)

    element_ref_map = []

    # Create a dictionary of elements -> refdata
    for el,eldata in basis_dict['basisSetElements'].items():
        ref = sorted(eldata['elementReferences'])

        for x in element_ref_map:
            if x['refkeys'] == ref:
                x['elements'].append(el)
                break
        else:
            element_ref_map.append({'refkeys': ref, 'elements': [el]})


    for item in element_ref_map:
        item['refdata'] = [ref_data[k] for k in item['refkeys']]
        item.pop('refkeys')

    return element_ref_map

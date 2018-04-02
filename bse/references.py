"""
Functions related to handling of references/citations
"""

from . import io


def compact_references(basis_dict, reffile_path):
    """
    Creates a mapping of elements to reference keys

    A list is returned, with each element being a dictionary
    with entries 'refdata' containing data for (possibly) multiple references,
    and 'elements' which is a list of element Z numbers
    that those references apply to

    Parameters
    ----------
    basis_dict : dict
        Dictionary containing basis set information
    reffile_path : str
        Full path to the JSON file containing reference information
    """

    ref_data = io.read_references(reffile_path)

    element_ref_map = []

    # Create a dictionary of elements -> refdata
    for el, eldata in basis_dict['basis_set_elements'].items():
        ref = sorted(eldata['element_references'])

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

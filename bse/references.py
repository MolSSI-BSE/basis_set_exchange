"""
Some helper functions related to handling of references/citations
"""

from . import io


def compact_references(basis_dict, reffile_path):
    """
    Creates a mapping of elements to reference keys

    A list is returned, with each element being a dictionary
    with entries 'ref_info' containing data for (possibly) multiple references,
    and 'elements' which is a list of element Z numbers
    that those references apply to

    Parameters
    ----------
    basis_dict : dict
        Dictionary containing basis set information
    reffile_path : str
        Full path to the JSON file containing reference information
    """

    ref_info = io.read_references(reffile_path)

    element_ref_map = []

    # Create a dictionary of elements -> ref_info
    for el, eldata in basis_dict['basis_set_elements'].items():
        ref_keys = eldata['element_references']

        for x in element_ref_map:
            if x['ref_info'] == ref_keys:
                x['elements'].append(el)
                break
        else:
            element_ref_map.append({'ref_info': ref_keys, 'elements': [el]})

    for item in element_ref_map:
        for refs in item['ref_info']:
            refs['reference_data'] = [ref_info[r] for r in refs['reference_keys']]

    return element_ref_map

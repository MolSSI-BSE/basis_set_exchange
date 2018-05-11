"""
Some helper functions related to handling of references/citations
"""

from . import io


def compact_references(basis_dict, reffile_path):
    """
    Creates a mapping of elements to reference keys

    A list is returned, with each element being a dictionary
    with entries 'reference_info' containing data for (possibly) multiple references,
    and 'elements' which is a list of element Z numbers
    that those references apply to

    Parameters
    ----------
    basis_dict : dict
        Dictionary containing basis set information
    reffile_path : str
        Full path to the JSON file containing reference information
    """

    allref_info = io.read_references(reffile_path)

    element_refs = []

    # Create a mapping of elements -> reference information
    for el, eldata in basis_dict['basis_set_elements'].items():

        # elref is a list of dict
        # dict is { 'reference_description': str, 'reference_keys': [keys] }
        elref = eldata['element_references']

        for x in element_refs:
            if x['reference_info'] == elref:
                x['elements'].append(el)
                break
        else:
            element_refs.append({'reference_info': elref, 'elements': [el]})

    for item in element_refs:

        # Loop over a list of dictionaries for this group of elements
        # Note that reference_data needs to be in the same order as the reference_keys
        for elref in item['reference_info']:
            elref['reference_data'] = {k: allref_info[k] for k in elref['reference_keys']}

    return element_refs

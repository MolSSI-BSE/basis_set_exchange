"""
Some helper functions related to handling of references/citations
"""

import textwrap


def compact_references(basis_dict, ref_data):
    """
    Creates a mapping of elements to reference keys

    A list is returned, with each element of the list being a dictionary
    with entries 'reference_info' containing data for (possibly) multiple references,
    and 'elements' which is a list of element Z numbers
    that those references apply to

    Parameters
    ----------
    basis_dict : dict
        Dictionary containing basis set information
    ref_data : dict
        Dictionary containing all reference information
    """

    element_refs = []

    # Create a mapping of elements -> reference information
    # (sort by Z first, keeping in mind Z is a string)
    sorted_el = sorted(basis_dict['elements'].items(), key=lambda x: int(x[0]))

    for el, eldata in sorted_el:

        # elref is a list of dict
        # dict is { 'reference_description': str, 'reference_keys': [keys] }
        elref = eldata['references']

        for x in element_refs:
            if x['reference_info'] == elref:
                x['elements'].append(el)
                break
        else:
            element_refs.append({'reference_info': elref, 'elements': [el]})

    for item in element_refs:
        # Loop over a list of dictionaries for this group of elements and add the
        # actual reference data
        # Since we store the keys with the data, we don't need it anymore
        for elref in item['reference_info']:
            elref['reference_data'] = [(k, ref_data[k]) for k in elref['reference_keys']]
            elref.pop('reference_keys')

    return element_refs


def reference_text(ref):
    '''Convert a single reference to plain text format

    Parameters
    ----------
    ref : dict
        Information about a single reference
    '''

    ref_wrap = textwrap.TextWrapper(initial_indent='', subsequent_indent=' ' * 8)

    s = ''
    if ref['type'] == 'unpublished':
        s += ref_wrap.fill(', '.join(ref['authors'])) + '\n'
        s += ref_wrap.fill(ref['title']) + '\n'
        s += ref_wrap.fill(ref['note']) + '\n'
    elif ref['type'] == 'article':
        s += ref_wrap.fill(', '.join(ref['authors'])) + '\n'
        s += ref_wrap.fill(ref['title']) + '\n'
        s += '{}, {}, {} ({})'.format(ref['journal'], ref['volume'], ref['page'], ref['year'])
        s += '\n' + ref['doi']
    elif ref['type'] == 'incollection':
        s += ref_wrap.fill(', '.join(ref['authors']))
        s += ref_wrap.fill('\n{}'.format(ref['title']))
        s += ref_wrap.fill('\nin \'{}\''.format(ref['booktitle']))
        if 'editors' in ref:
            s += ref_wrap.fill('\ned. ' + ', '.join(ref['editors']))
        if 'series' in ref:
            s += '\n{}, {}, {} ({})'.format(ref['series'], ref['volume'], ref['page'], ref['year'])
        if 'doi' in ref:
            s += '\n' + ref['doi']
    elif ref['type'] == 'techreport':
        s += ref_wrap.fill(', '.join(ref['authors']))
        s += ref_wrap.fill('\n{}'.format(ref['title']))
        s += '\n\'{}\''.format(ref['institution'])
        s += '\nTechnical Report {}'.format(ref['number'])
        s += '\n{}'.format(ref['year'])
        if 'doi' in ref:
            s += '\n' + ref['doi']
    elif ref['type'] == 'misc':
        s += ref_wrap.fill(', '.join(ref['authors'])) + '\n'
        s += ref_wrap.fill(ref['title'])
        if 'note' in ref:
            s += '\n' + ref['note']
        if 'doi' in ref:
            s += '\n' + ref['doi']
    else:
        raise RuntimeError('Cannot handle reference type {}'.format(ref['type']))
    return s

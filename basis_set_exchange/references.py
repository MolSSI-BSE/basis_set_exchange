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
    if ref['_entry_type'] == 'unpublished':
        s += ref_wrap.fill(', '.join(ref['authors'])) + '\n'
        if 'title' in ref:
            s += ref_wrap.fill(ref['title']) + '\n'
        if 'year' in ref:
            s += ref['year'] + ', '
        s += 'unpublished'
    elif ref['_entry_type'] == 'article':
        s += ref_wrap.fill(', '.join(ref['authors'])) + '\n'
        s += ref_wrap.fill(ref['title']) + '\n'
        s += '{}, {}, {} ({})'.format(ref['journal'], ref['volume'], ref['page'], ref['year'])
        s += '\n' + ref['doi']
    elif ref['_entry_type'] == 'incollection':
        s += ref_wrap.fill(', '.join(ref['authors']))
        s += '\n' + ref_wrap.fill('{}'.format(ref['title']))
        s += '\n' + ref_wrap.fill('in \'{}\''.format(ref['booktitle']))
        if 'editors' in ref:
            s += '\n' + ref_wrap.fill('ed. ' + ', '.join(ref['editors']))
        if 'series' in ref:
            s += '\n{}, {}, {} ({})'.format(ref['series'], ref['volume'], ref['page'], ref['year'])
        if 'doi' in ref:
            s += '\n' + ref['doi']
    elif ref['_entry_type'] == 'phdthesis':
        s += ref_wrap.fill(', '.join(ref['authors'])) + '\n'
        s += ref_wrap.fill(ref['title']) + '\n'
        s += '{}, {}'.format(ref.get('type', 'Ph.D. Thesis'), ref['school'])
    elif ref['_entry_type'] == 'techreport':
        s += ref_wrap.fill(', '.join(ref['authors'])) + '\n'
        s += '\n' + ref_wrap.fill('{}'.format(ref['title']))
        s += '\n\'{}\''.format(ref['institution'])
        s += '\n' + ref.get('type', 'Technical Report')
        if 'number' in ref:
            s += ' ' + ref['number']
        s += ', {}'.format(ref['year'])
        if 'doi' in ref:
            s += '\n' + ref['doi']
    elif ref['_entry_type'] == 'misc':
        s += ref_wrap.fill(', '.join(ref['authors'])) + '\n'
        s += ref_wrap.fill(ref['title'])
        if 'year' in ref:
            s += '\n' + ref['year']
        if 'doi' in ref:
            s += '\n' + ref['doi']
    else:
        raise RuntimeError('Cannot handle reference type {}'.format(ref['_entry_type']))
    if 'note' in ref:
        s += '\n' + ref_wrap.fill(ref['note'])
    return s

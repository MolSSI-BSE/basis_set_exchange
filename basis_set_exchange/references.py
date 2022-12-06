# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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


def reference_text(key, ref):
    '''Convert a single reference to plain text format

    Parameters
    ----------
    key : str
        Reference key (authorname2009a, etc)
    ref : dict
        Information about a single reference
    '''

    # Set up the text wrapping of the data (not the key)
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
        s += '{} {}, {} ({})'.format(ref['journal'], ref['volume'], ref['pages'], ref['year'])
        if 'doi' in ref:
            s += '\n' + ref['doi']
    elif ref['_entry_type'] == 'incollection':
        s += ref_wrap.fill(', '.join(ref['authors']))
        s += '\n' + ref_wrap.fill('{}'.format(ref['title']))
        s += '\n' + ref_wrap.fill('in \'{}\''.format(ref['booktitle']))
        if 'editors' in ref:
            s += '\n' + ref_wrap.fill('ed. ' + ', '.join(ref['editors']))
        if 'series' in ref:
            s += '\n{} {}, {} ({})'.format(ref['series'], ref['volume'], ref['pages'], ref['year'])
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

    # The final output has the key on its own line. The rest is indented by 4
    s = '\n'.join(' ' * 4 + x for x in s.splitlines())
    return key + '\n' + s

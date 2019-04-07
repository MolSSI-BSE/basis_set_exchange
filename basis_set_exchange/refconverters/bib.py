'''
Conversion of references to bibtex format
'''

import textwrap
from ..misc import compact_elements
from .common import get_library_citation


def _ref_bib(key, ref):
    '''Convert a single reference to bibtex format
    '''
    s = ''

    s += '@{}{{{},\n'.format(ref['type'], key)

    entry_lines = []
    for k, v in ref.items():
        if k == 'type':
            continue

        # Handle authors/editors
        if k == 'authors':
            entry_lines.append('    author = {{{}}}'.format(' and '.join(v)))
        elif k == 'editors':
            entry_lines.append('    editor = {{{}}}'.format(' and '.join(v)))
        else:
            entry_lines.append('    {} = {{{}}}'.format(k, v))

    s += ',\n'.join(entry_lines)
    s += '\n}'

    return s


def write_bib(refs):
    '''Converts references to bibtex
    '''

    full_str = ''

    lib_citation_desc, lib_citations = get_library_citation()

    full_str += '%' * 80 + '\n'
    full_str += textwrap.indent(lib_citation_desc, '% ')
    full_str += '%' * 80 + '\n\n'

    for k, r in lib_citations.items():
        full_str += _ref_bib(k, r) + '\n\n'

    full_str += '%' * 80 + '\n'
    full_str += "% References for the basis set\n"
    full_str += '%' * 80 + '\n'

    # First, write out the element, description -> key mapping
    # Also make a dict of unique reference to output
    unique_refs = {}

    for ref in refs:
        full_str += '% {}\n'.format(compact_elements(ref['elements']))

        for ri in ref['reference_info']:
            full_str += '%     {}\n'.format(ri['reference_description'])

            refdata = ri['reference_data']

            if len(refdata) == 0:
                full_str += '%     (...no reference...)\n%\n'
            else:
                rkeys = [x[0] for x in ri['reference_data']]
                full_str += '%         {}\n%\n'.format(' '.join(rkeys))

            for k, r in refdata:
                unique_refs[k] = r

    full_str += '\n\n'

    # Go through them sorted alphabetically by key
    for k, r in sorted(unique_refs.items(), key=lambda x: x[0]):
        full_str += '{}\n\n'.format(_ref_bib(k, r))

    return full_str

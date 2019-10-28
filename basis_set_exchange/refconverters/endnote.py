'''
Conversion of references to enw format
'''

import textwrap
from ..misc import compact_elements
from .common import get_library_citation


def _ref_endnote(key, ref):
    '''Convert a single reference to bibtex format
    '''
    s = '\n'

    if ref['_entry_type'] == 'article':
        s += "%0 Journal Article\n"
    elif ref['_entry_type'] == 'misc':
        s += "%0 Generic\n"
    elif ref['_entry_type'] == 'unpublished':
        s += "%0 Unpublished Work\n"
    elif ref['_entry_type'] == 'incollection':
        s += "%0 Book\n"
    elif ref['_entry_type'] == 'phdthesis':
        s += "%0 Thesis \n"
    elif ref['_entry_type'] == 'techreport':
        s += "%0 Report \n"
    else:
        s += "%0 Generic\n"


    entry_lines = []
    for k, v in ref.items():
        if k == '_entry_type':
            continue

        # Handle authors/editors
        if k == 'authors':
            for author in v:
                entry_lines.append('%A {}'.format(author))
        elif k == 'year':
            entry_lines.append('%D {}'.format(v))
        elif k == 'journal':
            entry_lines.append('%J {}'.format(v))
        elif k == 'volume':
            entry_lines.append('%V {}'.format(v))
        elif k == 'page':
            entry_lines.append('%P {}'.format(v))
        elif k == 'title':
            entry_lines.append('%T {}'.format(v))
        elif k == 'doi':
            entry_lines.append('%R {}'.format(v))
#If URL is to ever be added to BSE references
        #elif k == 'url':
            #entry_lines.append('%U {}'.format(v))
        else:
            entry_lines.append('    {} = {{{}}}'.format(k, v))

    s += '\n'.join(entry_lines)
    s += '\n'

    return s


def write_endnote(refs):
    '''Converts references to endnote
    '''

    full_str = ''

    lib_citation_desc, lib_citations = get_library_citation()

    full_str += '%' * 80 + '\n'
    full_str += textwrap.indent(lib_citation_desc, '% ')
    full_str += '%' * 80 + '\n\n'

    for k, r in lib_citations.items():
        full_str += _ref_endnote(k, r) + '\n\n'

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
                full_str += '%         (...no reference...)\n%\n'
            else:
                rkeys = [x[0] for x in ri['reference_data']]
                full_str += '%         {}\n%\n'.format(' '.join(rkeys))

            for k, r in refdata:
                unique_refs[k] = r

    full_str += '\n\n'

    # Go through them sorted alphabetically by key
    for k, r in sorted(unique_refs.items(), key=lambda x: x[0]):
        full_str += '{}\n\n'.format(_ref_endnote(k, r))

    return full_str

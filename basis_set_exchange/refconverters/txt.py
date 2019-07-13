'''
Conversion of references to plain text format
'''

import textwrap
from ..misc import compact_elements
from ..references import reference_text
from .common import get_library_citation


def write_txt(refs):
    '''Converts references to plain text format
    '''
    full_str = '\n'

    lib_citation_desc, lib_citations = get_library_citation()

    # Add the refs for the libarary at the top
    full_str += '*' * 80 + '\n'
    full_str += lib_citation_desc
    full_str += '*' * 80 + '\n'
    for r in lib_citations.values():
        ref_txt = reference_text(r)
        ref_txt = textwrap.indent(ref_txt, ' ' * 4)
        full_str += '{}\n\n'.format(ref_txt)

    full_str += '*' * 80 + '\n'
    full_str += "References for the basis set\n"
    full_str += '*' * 80 + '\n'

    # First, write out the element, description -> key mapping
    # Also make a dict of unique reference to output
    unique_refs = {}

    for ref in refs:
        full_str += '# {}\n'.format(compact_elements(ref['elements']))

        for ri in ref['reference_info']:
            full_str += '#     {}\n'.format(ri['reference_description'])

            refdata = ri['reference_data']

            if len(refdata) == 0:
                full_str += '#         (...no reference...)\n%\n'
            else:
                rkeys = [x[0] for x in ri['reference_data']]
                full_str += '#         {}\n#\n'.format(' '.join(rkeys))

            for k, r in refdata:
                unique_refs[k] = r

    full_str += '\n\n'

    # Go through them sorted alphabetically by key
    for k, r in sorted(unique_refs.items(), key=lambda x: x[0]):
        full_str += k + '\n'
        ref_txt = reference_text(r)
        ref_txt = textwrap.indent(ref_txt, ' ' * 4)
        full_str += '{}\n\n'.format(ref_txt)

    return full_str

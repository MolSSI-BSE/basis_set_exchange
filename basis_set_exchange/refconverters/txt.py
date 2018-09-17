'''
Conversion of references to plain text format
'''

import textwrap
from ..misc import compact_elements
from ..references import reference_text


def write_txt(refs):
    '''Converts references to plain text format
    '''
    full_str = u'** ' + '\n\n'
    for ref in refs:
        full_str += u'{}\n'.format(compact_elements(ref['elements']))

        for ri in ref['reference_info']:
            full_str += u'    ## {}\n'.format(ri['reference_description'])

            refdata = ri['reference_data']

            if len(refdata) == 0:
                full_str += u'    (...no reference...)\n\n'
            for k, r in refdata.items():
                ref_txt = reference_text(r)
                ref_txt = textwrap.indent(ref_txt, ' ' * 4)
                full_str += u'{}\n\n'.format(ref_txt)

    return full_str

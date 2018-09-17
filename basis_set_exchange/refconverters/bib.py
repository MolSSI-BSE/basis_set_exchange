'''
Conversion of references to bibtex format
'''

from ..misc import compact_elements


def _ref_bib(key, ref):
    '''Convert a single reference to bibtex format
    '''
    s = u''

    s += u'@{}{{{},\n'.format(ref['type'], key)

    entry_lines = []
    for k, v in ref.items():
        if k == 'type':
            continue

        # Handle authors/editors
        if k == 'authors':
            entry_lines.append(u'    author = {{{}}}'.format(' and '.join(v)))
        elif k == 'editors':
            entry_lines.append(u'    editor = {{{}}}'.format(' and '.join(v)))
        else:
            entry_lines.append(u'    {} = {{{}}}'.format(k, v))

    s += ',\n'.join(entry_lines)
    s += '\n}'

    return s


def write_bib(refs):
    '''Converts references to bibtex
    '''

    full_str = u''

    # First, write out the element, description -> key mapping
    # Also make a dict of unique reference to output
    unique_refs = {}

    for ref in refs:
        full_str += u'% {}\n'.format(compact_elements(ref['elements']))

        for ri in ref['reference_info']:
            full_str += u'%     {}\n'.format(ri['reference_description'])

            refdata = ri['reference_data']

            if len(refdata) == 0:
                full_str += u'%     (...no reference...)\n%\n'
            else:
                full_str += u'%         {}\n%\n'.format(' '.join(ri['reference_keys']))

            for k, r in refdata.items():
                unique_refs[k] = r

    full_str += u'\n\n'

    # Go through them sorted alphabetically by key
    for k, r in sorted(unique_refs.items(), key=lambda x: x[0]):
        full_str += u'{}\n\n'.format(_ref_bib(k, r))

    return full_str

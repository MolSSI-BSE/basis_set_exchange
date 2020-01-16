'''
Conversion of references to bibtex format
'''


def write_bib(key, ref):
    '''Convert a single reference to bibtex format
    '''
    s = ''

    s += '@{}{{{},\n'.format(ref['_entry_type'], key)

    entry_lines = []
    for k, v in ref.items():
        if k == '_entry_type':
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

'''                                                                                                      
Conversion of references to enw format                                                                                              
'''


def write_endnote(key, ref):
    '''Convert a single reference to RIS format                                                                                  
    '''
    s = ''

    s += '  \n'.format(ref['_entry_type'], key)
    if ref['_entry_type'] == 'article':
        s += "%0 Journal Article \n"
    elif ref['_entry_type'] == 'misc':
        s += "%0 Generic \n"
    elif ref['_entry_type'] == 'unpublished':
        s += "%0 Unpublished \n"
    elif ref['_entry_type'] == 'incollection':
        s += "%0 Book \n"
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
        else:
            entry_lines.append('%Z {}:{}'.format(k, v))

    s += '\n'.join(entry_lines)
    s += '\n'

    return s

'''                                                                                                      
Conversion of references to ris format                                                                                              
'''


def write_ris(key, ref):
    '''Convert a single reference to ris format                                                                                  
    '''
    s = ''

    s += '  \n'.format(ref['_entry_type'], key)
    if ref['_entry_type'] == 'article':
        s += "TY Journal Article \n"
    elif ref['_entry_type'] == 'misc':
        s += "TY Generic \n"
    elif ref['_entry_type'] == 'unpublished':
        s += "TY Unpublished \n"
    elif ref['_entry_type'] == 'incollection':
        s += "TY Book \n"
    elif ref['_entry_type'] == 'phdthesis':
        s += "TY Thesis \n"
    elif ref['_entry_type'] == 'techreport':
        s += "TY Report \n"
    else:
        s += "TY Generic\n"

    entry_lines = []
    for k, v in ref.items():
        if k == '_entry_type':
            continue

        # Handle authors/editors
        if k == 'authors':
            for author in v:
                entry_lines.append('AU {}'.format(author))
        elif k == 'year':
            entry_lines.append('PY {}'.format(v))
        elif k == 'journal':
            entry_lines.append('JO {}'.format(v))
        elif k == 'volume':
            entry_lines.append('VL {}'.format(v))
        elif k == 'page':
            entry_lines.append('SP {}'.format(v))
        elif k == 'title':
            entry_lines.append('T1 {}'.format(v))
        elif k == 'doi':
            entry_lines.append('DO {}'.format(v))
        else:
            entry_lines.append('N1 {}:{}'.format(k, v))

    s += '\n'.join(entry_lines)
    s += '\n'

    return s

from .common import *

def ref_txt(ref):
    s = u'    '
    if ref['type'] == 'article':
        s += u', '.join(ref['authors'])
        s += u'\n    {}, {}, {} ({})'.format(ref['journal'], ref['volume'], ref['page'], ref['year'])
        s += u'\n    ' + ref['doi']
    elif ref['type'] == 'incollection':
        s += u', '.join(ref['authors'])
        s += u'\n    {}'.format(ref['title'])
        s += u'\n    in \'{}\''.format(ref['booktitle'])
        if 'editors' in ref:
            s += u'\n    ed. ' + u', '.join(ref['editors'])
        if 'series' in ref:
            s += u'\n    {}, {}, {} ({})'.format(ref['series'], ref['volume'], ref['page'], ref['year'])
        if 'doi' in ref:
            s += u'\n    ' + ref['doi']
    else:
        raise RuntimeError('Cannot handle reference type {}'.format(ref['type']))
    return s

def write_txt(refs):
    full_str = u''
    for refinfo in refs:
        full_str += u'{}\n'.format(compact_elements(refinfo['elements']))

        if len(refinfo['refdata']) == 0:
            full_str += u'    (...no reference...)\n\n'
        for r in refinfo['refdata']:
            full_str += u'{}\n\n'.format(ref_txt(r))

    return full_str


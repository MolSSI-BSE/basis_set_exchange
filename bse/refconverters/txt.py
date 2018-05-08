'''
Conversion of references to plain text format
'''

from .common import *


def _ref_txt(ref):
    '''Convert a single reference to plain text format
    '''
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
    elif ref['type'] == 'techreport':
        print(ref)
        s += u', '.join(ref['authors'])
        s += u'\n    {}'.format(ref['title'])
        s += u'\n    \'{}\''.format(ref['institution'])
        s += u'\n    Technical Report {}'.format(ref['number'])
        s += u'\n    {}'.format(ref['year'])
        if 'doi' in ref:
            s += u'\n    ' + ref['doi']
    else:
        raise RuntimeError('Cannot handle reference type {}'.format(ref['type']))
    return s


def write_txt(refs):
    '''Converts references to plain text format
    '''
    full_str = u''
    for refinfo in refs:
        full_str += u'{}\n'.format(compact_elements(refinfo['elements']))

        if len(refinfo['ref_info']) == 0:
            full_str += u'    (...no reference...)\n\n'
        for rd in refinfo['ref_info']:
            full_str += u'    ## {}\n'.format(rd['reference_description'])

            for r in rd['reference_data']:
                full_str += u'{}\n\n'.format(_ref_txt(r))

    return full_str

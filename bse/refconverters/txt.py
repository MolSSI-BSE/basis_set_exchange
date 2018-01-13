from .common import *

def ref_txt(ref):
    s = "    "
    if ref['type'] == 'article':
        s += ', '.join(ref['authors'])
        s += '\n    {}, {}, {} ({})'.format(ref['journal'], ref['volume'], ref['page'], ref['year'])
        s += '\n    ' + ref['doi']
    else:
        raise RuntimeError("Cannot handle reference type '{}'".format(ref['type']))
    return s

def write_txt(refs):
    full_str = ""
    for refinfo in refs:
        full_str += "{}\n".format(compact_elements(refinfo['elements']))

        if len(refinfo['refdata']) == 0:
            full_str += "    (...no reference...)\n"
        for r in refinfo['refdata']:
            full_str += "{}\n\n".format(ref_txt(r))

    return full_str


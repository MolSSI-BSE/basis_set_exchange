'''
Converts basis set data to a specified output format
'''

from collections import OrderedDict
from .bib import write_bib
from .txt import write_txt
from .bsejson import write_json

_converter_map = {
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'comment': None,
        'function': write_json
    },
    'bib': {
        'display': 'BibTeX',
        'extension': '.bib',
        'comment': '%',
        'function': write_bib
    },
    'txt': {
        'display': 'Plain Text',
        'extension': '.txt',
        'comment': '',
        'function': write_txt
    }
}


def convert_references(ref_dict, fmt, header=None):
    '''
    Returns the basis set references as a string representing
    the data in the specified output format
    '''

    # Make fmt case insensitive
    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown reference format "{}"'.format(fmt))

    ret_str = _converter_map[fmt]['function'](ref_dict)
    if header is not None and fmt != 'json':
        comment_str = _converter_map[fmt]['comment']
        header_str = comment_str + comment_str.join(header.splitlines(True))
        ret_str = header_str + '\n\n' + ret_str

    return ret_str


def get_formats():
    '''
    Returns the available reference formats mapped to display name.

    This is returned as an ordered dictionary, with the most common
    at the top, followed by the rest in alphabetical order
    '''

    at_top = ['bib', 'txt']
    ret = [(k, v['display']) for k, v in _converter_map.items()]
    ret = OrderedDict(sorted(ret))

    for x in reversed(at_top):
        ret.move_to_end(x, False)

    # Move JSON to the end
    ret.move_to_end('json', True)

    return ret


def get_format_extension(fmt):
    '''
    Returns the recommended extension for a given format
    '''

    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))

    return _converter_map[fmt]['extension']

'''
Converts basis set data to a specified output format
'''

from .. import sort
from .bib import write_bib
from .txt import write_txt
from .bsejson import write_json

_converter_map = {
    'txt': {
        'display': 'Plain Text',
        'extension': '.txt',
        'comment': '',
        'function': write_txt
    },
    'bib': {
        'display': 'BibTeX',
        'extension': '.bib',
        'comment': '%',
        'function': write_bib
    },
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'comment': None,
        'function': write_json
    }
}


def convert_references(ref_data, fmt):
    '''
    Returns the basis set references as a string representing
    the data in the specified output format
    '''

    # Make fmt case insensitive
    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown reference format "{}"'.format(fmt))

    # Sort the data for all references
    for elref in ref_data:
        for rinfo in elref['reference_info']:
            rdata = rinfo['reference_data']
            rinfo['reference_data'] = [(k, sort.sort_single_reference(v)) for k, v in rdata]

    # Actually do the conversion
    ret_str = _converter_map[fmt]['function'](ref_data)

    return ret_str


def get_formats():
    '''
    Returns the available reference formats mapped to display name.

    This is returned as an ordered dictionary, with the most common
    at the top, followed by the rest in alphabetical order
    '''

    return {k: v['display'] for k, v in _converter_map.items()}


def get_format_extension(fmt):
    '''
    Returns the recommended extension for a given format
    '''

    if fmt is None:
        return 'dict'

    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))

    return _converter_map[fmt]['extension']

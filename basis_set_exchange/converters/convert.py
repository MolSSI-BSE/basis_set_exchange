'''
Converts basis set data to a specified output format
'''

from collections import OrderedDict
from .bsejson import write_json
from .nwchem import write_nwchem
from .g94 import write_g94
from .gamess_us import write_gamess_us
from .psi4 import write_psi4
from .turbomole import write_turbomole

_converter_map = {
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'comment': None,
        'function': write_json
    },
    'nwchem': {
        'display': 'NWChem',
        'extension': '.nw',
        'comment': '#',
        'function': write_nwchem
    },
    'gaussian94': {
        'display': 'Gaussian94',
        'extension': '.gbs',
        'comment': '!',
        'function': write_g94
    },
    'gamess_us': {
        'display': 'GAMESS US',
        'extension': '.bas',
        'comment': '!',
        'function': write_gamess_us
    },
    'psi4': {
        'display': 'Psi4',
        'extension': '.gbs',
        'comment': '!',
        'function': write_psi4
    },
    'turbomole': {
        'display': 'Turbomole',
        'extension': '.tm',
        'comment': '#',
        'function': write_turbomole
    }
}


def convert_basis(basis_dict, fmt, header=None):
    '''
    Returns the basis set data as a string representing
    the data in the specified output format
    '''

    # make converters case insensitive
    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))

    ret_str = _converter_map[fmt]['function'](basis_dict)
    if header is not None and fmt != 'json':
        comment_str = _converter_map[fmt]['comment']
        header_str = comment_str + comment_str.join(header.splitlines(True))
        ret_str = header_str + '\n\n' + ret_str

    # HACK - Psi4 requires the first non-comment line be spherical/cartesian
    #        so we have to add that before the header
    if fmt == 'psi4':
        ret_str = basis_dict['basis_set_harmonic_type'] + '\n\n' + ret_str

    return ret_str


def get_formats():
    '''
    Returns the available formats mapped to display name.

    This is returned as an ordered dictionary, with the most common
    at the top, followed by the rest in alphabetical order
    '''

    at_top = ['nwchem', 'gaussian94', 'psi4']
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

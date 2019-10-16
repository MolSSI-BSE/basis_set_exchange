'''
Converts basis set data to a specified output format
'''

from .bsejson import write_json
from .nwchem import write_nwchem
from .g94 import write_g94, write_xtron
from .gamess_us import write_gamess_us
from .gamess_uk import write_gamess_uk
from .psi4 import write_psi4
from .qchem import write_qchem
from .orca import write_orca
from .turbomole import write_turbomole
from .molpro import write_molpro
from .molcas import write_molcas
from .genbas import write_cfour, write_aces2
from .dalton import write_dalton
from .qcschema import write_qcschema
from .demon2k import write_demon2k
from .pqs import write_pqs
from .cp2k import write_cp2k
from .bsedebug import write_bsedebug
from .bdf import write_bdf

_converter_map = {
    'nwchem': {
        'display': 'NWChem',
        'extension': '.nw',
        'comment': '#',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_nwchem
    },
    'gaussian94': {
        'display': 'Gaussian',
        'extension': '.gbs',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_g94
    },
    'psi4': {
        'display': 'Psi4',
        'extension': '.gbs',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_psi4
    },
    'molcas': {
        'display': 'Molcas',
        'extension': '.molcas',
        'comment': '*',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_molcas
    },
    'qchem': {
        'display': 'Q-Chem',
        'extension': '.qchem',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_qchem
    },
    'orca': {
        'display': 'ORCA',
        'extension': '.orca',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_orca
    },
    'dalton': {
        'display': 'Dalton',
        'extension': '.dalton',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_dalton
    },
    'qcschema': {
        'display': 'QCSchema',
        'extension': '.json',
        'comment': None,
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_qcschema
    },
    'cp2k': {
        'display': 'CP2K',
        'extension': '.cp2k',
        'comment': '#',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_cp2k
    },
    'pqs': {
        'display': 'PQS',
        'extension': '.pqs',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_pqs
    },
    'demon2k': {
        'display': 'deMon2K',
        'extension': '.d2k',
        'comment': '#',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_demon2k
    },
    'gamess_us': {
        'display': 'GAMESS US',
        'extension': '.bas',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_gamess_us
    },
    'turbomole': {
        'display': 'Turbomole',
        'extension': '.tm',
        'comment': '#',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_turbomole
    },
    'gamess_uk': {
        'display': 'GAMESS UK',
        'extension': '.bas',
        'comment': '#',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_gamess_uk
    },
    'molpro': {
        'display': 'Molpro',
        'extension': '.mpro',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_molpro
    },
    'cfour': {
        'display': 'CFOUR',
        'extension': '.c4bas',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_cfour
    },
    'acesii': {
        'display': 'ACES II',
        'extension': '.acesii',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_aces2
    },
    'xtron': {
        'display': 'xTron',
        'extension': '.gbs',
        'comment': '!',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_xtron
    },
    'bsedebug': {
        'display': 'BSE Debug',
        'extension': '.bse',
        'comment': '!',
        'valid': None,
        'function': write_bsedebug
    },
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'comment': None,
        'valid': None,
        'function': write_json
    },
    'bdf': {
        'display': 'BDF',
        'extension': '.bdf',
        'comment': '*',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_bdf
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

    converter = _converter_map[fmt]

    # Determine if the converter supports all the types in the basis_dict
    if converter['valid'] is not None:
        ftypes = set(basis_dict['function_types'])
        if not ftypes <= converter['valid']:
            raise RuntimeError('Converter {} does not support all function types: {}'.format(fmt, str(ftypes)))

    # Actually do the conversion
    ret_str = converter['function'](basis_dict)

    # Don't add a header for QCSchema, JSON, etc
    if header is not None and _converter_map[fmt]['comment'] is not None:
        comment_str = _converter_map[fmt]['comment']
        header_str = comment_str + comment_str.join(header.splitlines(True))
        ret_str = header_str + '\n\n' + ret_str

    # HACK - Psi4 requires the first non-comment line be spherical/cartesian
    #        so we have to add that before the header
    if fmt == 'psi4':
        types = basis_dict['function_types']
        harm_type = 'spherical' if 'gto_spherical' in types else 'cartesian'
        ret_str = harm_type + '\n\n' + ret_str

    return ret_str


def get_formats(function_types=None):
    '''
    Returns the available formats mapped to display name.

    This is returned as an ordered dictionary, with the most common
    at the top, followed by the rest in alphabetical order

    If a list is specified for function_types, only those formats
    supporting the given function types will be returned.
    '''

    if function_types is None:
        return {k: v['display'] for k, v in _converter_map.items()}

    ftypes = [x.lower() for x in function_types]
    ftypes = set(ftypes)
    ret = []

    for fmt, v in _converter_map.items():
        if v['valid'] is None or ftypes <= v['valid']:
            ret.append(fmt)
    return ret


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

# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''
Driver for converting basis set data to a specified output format
'''

import bz2
from .bsejson import write_json
from .nwchem import write_nwchem
from .g94 import write_g94, write_g94lib, write_xtron, write_psi4
from .gamess_us import write_gamess_us
from .gamess_uk import write_gamess_uk
from .qchem import write_qchem
from .orca import write_orca
from .turbomole import write_turbomole
from .molpro import write_molpro
from .libmol import write_libmol
from .molcas import write_molcas
from .molcas_library import write_molcas_library
from .genbas import write_cfour, write_aces2
from .dalton import write_dalton
from .qcschema import write_qcschema
from .demon2k import write_demon2k
from .pqs import write_pqs
from .cp2k import write_cp2k
from .bsedebug import write_bsedebug
from .bdf import write_bdf
from .ricdwrap import write_ricdwrap
from .fhiaims import write_fhiaims
from .jaguar import write_jaguar
from .crystal import write_crystal
from .veloxchem import write_veloxchem
from .tonto import write_tonto

_writer_map = {
    'nwchem': {
        'display': 'NWChem',
        'extension': '.nw',
        'comment': '#',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_nwchem
    },
    'gaussian94': {
        'display': 'Gaussian',
        'extension': '.gbs',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_g94
    },
    'gaussian94lib': {
        'display': 'Gaussian, system library',
        'extension': '.gbs',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_g94lib
    },
    'psi4': {
        'display': 'Psi4',
        'extension': '.gbs',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_psi4
    },
    'molcas': {
        'display': 'Molcas',
        'extension': '.molcas',
        'comment': '*',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_molcas
    },
    'molcas_library': {
        'display': 'Molcas basis_library',
        'extension': '.molcas',
        'comment': '*',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_molcas_library
    },
    'qchem': {
        'display': 'Q-Chem',
        'extension': '.qchem',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_qchem
    },
    'orca': {
        'display': 'ORCA',
        'extension': '.orca',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_orca
    },
    'dalton': {
        'display': 'Dalton',
        'extension': '.dalton',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_dalton
    },
    'qcschema': {
        'display': 'QCSchema',
        'extension': '.json',
        'comment': None,
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_qcschema
    },
    'cp2k': {
        'display': 'CP2K',
        'extension': '.cp2k',
        'comment': '#',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_cp2k
    },
    'pqs': {
        'display': 'PQS',
        'extension': '.pqs',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_pqs
    },
    'demon2k': {
        'display': 'deMon2K',
        'extension': '.d2k',
        'comment': '#',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_demon2k
    },
    'gamess_us': {
        'display': 'GAMESS US',
        'extension': '.bas',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_gamess_us
    },
    'turbomole': {
        'display': 'Turbomole',
        'extension': '.tm',
        'comment': '#',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_turbomole
    },
    'gamess_uk': {
        'display': 'GAMESS UK',
        'extension': '.bas',
        'comment': '#',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_gamess_uk
    },
    'molpro': {
        'display': 'Molpro',
        'extension': '.mpro',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_molpro
    },
    'libmol': {
        'display': 'Molpro system library',
        'extension': '.libmol',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_libmol
    },
    'cfour': {
        'display': 'CFOUR',
        'extension': '.c4bas',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_cfour
    },
    'acesii': {
        'display': 'ACES II',
        'extension': '.acesii',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_aces2
    },
    'xtron': {
        'display': 'xTron',
        'extension': '.gbs',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
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
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_bdf
    },
    'ricdwrap': {
        'display': 'Wrapper for generating acCD auxiliary basis sets with OpenMolcas',
        'extension': '.ricdwrap',
        'comment': '*',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_ricdwrap
    },
    'fhiaims': {
        'display': 'FHI-aims',
        'extension': '.fhiaims',
        'comment': '#',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical'},
        'function': write_fhiaims
    },
    'jaguar': {
        'display': 'Jaguar',
        'extension': '.jaguar',
        'comment': '#',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_jaguar
    },
    'crystal': {
        'display': 'Crystal',
        'extension': '.crystal',
        'comment': '*',
        'valid': set(['gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp']),
        'function': write_crystal
    },
    'veloxchem': {
        'display': 'VeloxChem',
        'extension': '.vlx',
        'comment': '!',
        'valid': {'gto', 'gto_spherical'},
        'function': write_veloxchem
    },
    'tonto': {
        'display': 'Wrapper for generating tonto auxiliary basis sets',
        'extension': '',
        'comment': '!',
        'valid': {'gto', 'gto_cartesian', 'gto_spherical', 'scalar_ecp'},
        'function': write_tonto
    },
}


def write_formatted_basis_str(basis_dict, fmt, header=None):
    '''
    Returns the basis set data as a string representing
    the data in the specified output format
    '''

    # make writers case insensitive
    fmt = fmt.lower()
    if fmt not in _writer_map:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))

    writer = _writer_map[fmt]

    # Determine if the writer supports all the types in the basis_dict
    if writer['valid'] is not None:
        ftypes = set(basis_dict['function_types'])
        if not ftypes <= writer['valid']:
            raise RuntimeError('Converter {} does not support all function types: {}'.format(fmt, str(ftypes)))

    # Actually do the conversion
    ret_str = writer['function'](basis_dict)

    # Don't add a header for QCSchema, JSON, etc
    if header is not None and _writer_map[fmt]['comment'] is not None:
        comment_str = _writer_map[fmt]['comment']
        header_str = comment_str + comment_str.join(header.splitlines(True))

        # HACK - Gaussian94Lib doesn't tolerate blank lines after the header
        if fmt == 'gaussian94lib':
            ret_str = header_str + ret_str
        else:
            ret_str = header_str + '\n\n' + ret_str

    # HACK - Psi4 requires the first non-comment line be spherical/cartesian
    #        so we have to add that before the header
    if fmt == 'psi4':
        types = basis_dict['function_types']
        harm_type = 'cartesian' if 'gto_cartesian' in types else 'spherical'
        ret_str = harm_type + '\n\n' + ret_str

    return ret_str


def write_formatted_basis_file(basis_dict, outfile_path, basis_fmt=None, header=None):
    if basis_fmt is None:
        for k, v in _writer_map.items():
            ext = v['extension']
            ext_bz2 = ext + '.bz2'
            if outfile_path.endswith(ext) or outfile_path.endswith(ext_bz2):
                basis_fmt = k
                break
        else:
            raise RuntimeError("Unable to determine basis set format of '{}'".format(outfile_path))
    else:
        basis_fmt = basis_fmt.lower()

    if basis_fmt not in _writer_map:
        raise RuntimeError("Unknown output file format '{}'".format(basis_fmt))

    basis_str = write_formatted_basis_str(basis_dict, basis_fmt, header)

    if outfile_path.endswith('.bz2'):
        with bz2.open(outfile_path, 'wt') as f:
            f.write(basis_str)
    else:
        with open(outfile_path, 'w') as f:
            f.write(basis_str)


def get_writer_formats(function_types=None):
    '''Return information about the basis set formats available for writing

    The returned data is a map of format to display name. The format
    can be passed as the fmt argument to :func:`write_formatted_basis_str` or
    :func:`write_formatted_basis_file`

    If a list is specified for function_types, only those formats
    supporting the given function types will be returned.
    '''

    if function_types is None:
        return {k: v['display'] for k, v in _writer_map.items()}

    ftypes = [x.lower() for x in function_types]
    ftypes = set(ftypes)
    ret = {}

    for fmt, v in _writer_map.items():
        if v['valid'] is None or ftypes <= v['valid']:
            ret[fmt] = v['display']
    return ret


def get_format_extension(fmt):
    '''
    Returns the recommended extension for a given format
    '''

    if fmt is None:
        return 'dict'

    fmt = fmt.lower()
    if fmt not in _writer_map:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))

    return _writer_map[fmt]['extension']

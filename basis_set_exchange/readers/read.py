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
Read a basis set file in a given format
'''

import os
import bz2
from ..skel import create_skel
from ..validator import validate_data
from ..compose import _whole_basis_types
from .turbomole import read_turbomole
from .g94 import read_g94
from .nwchem import read_nwchem
from .gbasis import read_gbasis
from .dalton import read_dalton
from .molcas import read_molcas
from .molpro import read_molpro
from .libmol import read_libmol
from .genbas import read_genbas
from .demon2k import read_demon2k
from .ricdlib import read_ricdlib
from .gamess_us import read_gamess_us
from .cp2k import read_cp2k
from .crystal import read_crystal
from .veloxchem import read_veloxchem

_reader_map = {
    'turbomole': {
        'display': 'Turbomole',
        'extension': '.tm',
        'reader': read_turbomole
    },
    'gaussian94': {
        'display': 'Gaussian94',
        'extension': '.gbs',
        'reader': read_g94
    },
    'nwchem': {
        'display': 'NWChem',
        'extension': '.nw',
        'reader': read_nwchem
    },
    'dalton': {
        'display': 'Dalton',
        'extension': '.mol',
        'reader': read_dalton
    },
    'molcas': {
        'display': 'Molcas',
        'extension': '.molcas',
        'reader': read_molcas
    },
    # for now this is just an alias for molcas, as it seems to work fine
    'molcas_library': {
        'display': 'Molcas basis_library',
        'extension': '.molcas',
        'reader': read_molcas
    },
    'molpro': {
        'display': 'Molpro',
        'extension': '.mpro',
        'reader': read_molpro
    },
    'libmol': {
        'display': 'Molpro system library',
        'extension': '.libmol',
        'reader': read_libmol
    },
    'cfour': {
        'display': 'CFOUR',
        'extension': '.c4bas',
        'reader': read_genbas
    },
    'genbas': {
        'display': 'Genbas',
        'extension': '.genbas',
        'reader': read_genbas
    },
    'gbasis': {
        'display': 'GBasis',
        'extension': '.gbasis',
        'reader': read_gbasis
    },
    'demon2k': {
        'display': 'deMon2k',
        'extension': '.d2k',
        'reader': read_demon2k
    },
    'ricdlib': {
        'display': 'MolCAS RICDlib',
        'extension': '.RICDLib',
        'reader': read_ricdlib
    },
    'gamess_us': {
        'display': 'GAMESS US',
        'extension': '.bas',
        'reader': read_gamess_us
    },
    'cp2k': {
        'display': 'CP2K',
        'extension': '.cp2k',
        'reader': read_cp2k
    },
    'crystal': {
        'display': 'Crystal',
        'extension': '.crystal',
        'reader': read_crystal
    },
    'veloxchem': {
        'display': 'VeloxChem',
        'extension': '.vlx',
        'reader': read_veloxchem
    }
}


def _fix_uncontracted(basis):
    '''
    Forces the contraction coefficient of uncontracted shells to 1.0
    '''

    for el in basis['elements'].values():
        if 'electron_shells' not in el:
            continue

        for sh in el['electron_shells']:
            if len(sh['coefficients']) == 1 and len(sh['coefficients'][0]) == 1:
                sh['coefficients'][0][0] = '1.0000000'

            # Some uncontracted shells don't have a coefficient
            if len(sh['coefficients']) == 0:
                sh['coefficients'].append(['1.0000000'])

    return basis


def read_formatted_basis_str(basis_str, basis_fmt, validate=False, as_component=False):
    basis_lines = [x.strip() for x in basis_str.splitlines()]

    return_values = _reader_map[basis_fmt]['reader'](basis_lines)
    element_data, other_data = return_values

    # the readers give the 'elements' member of a basis set json
    # We need to do a little fixing up
    if as_component:
        data = create_skel('component')
        data['elements'] = element_data
        for el in data['elements'].values():
            el['references'] = []
        bs_type = 'component'
    else:
        data = create_skel('minimal')
        data['elements'] = element_data
        data['name'] = other_data.get('name', 'unknown_basis')
        data['description'] = other_data.get('description', 'no_description')
        bs_type = 'minimal'

        # Create the function types
        data['function_types'] = _whole_basis_types(data)

    # It's debatable if I want to do this
    #return _fix_uncontracted(data)

    # Validate if desired
    if validate:
        validate_data(bs_type, data)

    return data


def read_formatted_basis_file(file_path, basis_fmt=None, encoding='utf-8-sig', validate=False, as_component=False):
    # Note that the default is utf-8-sig, which handles the optional byte order mark

    if not os.path.isfile(file_path):
        raise RuntimeError('Basis file path \'{}\' does not exist'.format(file_path))

    if basis_fmt is None:
        for k, v in _reader_map.items():
            ext = v['extension']
            ext_bz2 = ext + '.bz2'
            if file_path.endswith(ext) or file_path.endswith(ext_bz2):
                basis_fmt = k
                break

        else:
            raise RuntimeError("Unable to determine basis set format of '{}'".format(file_path))
    else:
        basis_fmt = basis_fmt.lower()

    if basis_fmt not in _reader_map:
        raise RuntimeError("Unknown file format to read '{}'".format(basis_fmt))

    # Handle compressed files
    if file_path.endswith('.bz2'):
        with bz2.open(file_path, 'rt', encoding=encoding) as f:
            basis_str = f.read()
    else:
        with open(file_path, 'r', encoding=encoding) as f:
            basis_str = f.read()

    return read_formatted_basis_str(basis_str, basis_fmt, validate, as_component)


def get_reader_formats():
    '''
    Returns the basis set formats that can be read by this library.

    This is returned as an ordered dictionary of key to display name.
    '''

    return {k: v['display'] for k, v in _reader_map.items()}

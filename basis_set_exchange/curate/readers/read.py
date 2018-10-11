'''
Read a basis set file in a given format
'''

import os
import bz2
from .turbomole import read_turbomole
from .g94 import read_g94
from .nwchem import read_nwchem
from .gbasis import read_gbasis

_type_readers = {
    'turbomole': {
        'reader': read_turbomole,
        'extension': '.tm',
    },
    'gaussian94': {
        'reader': read_g94,
        'extension': '.gbs'
    },
    'nwchem': {
        'reader': read_nwchem,
        'extension': '.nw'
    },
    'gbasis': {
        'reader': read_gbasis,
        'extension': '.gbasis'
    }
}


def _fix_uncontracted(basis):
    '''
    Forces the contraction coefficient of uncontracted shells to 1.0
    '''

    for el in basis['basis_set_elements'].values():
        if 'element_electron_shells' not in el:
            continue

        for sh in el['element_electron_shells']:
            if len(sh['shell_coefficients']) == 1 and len(sh['shell_coefficients'][0]) == 1:
                sh['shell_coefficients'][0][0] = '1.0000000'

            # Some uncontracted shells don't have a coefficient
            if len(sh['shell_coefficients']) == 0:
                sh['shell_coefficients'].append(['1.0000000'])

    return basis


def read_formatted_basis(file_path, file_type=None):

    if not os.path.isfile(file_path):
        raise RuntimeError('Basis file path \'{}\' does not exist'.format(file_path))

    if file_type is None:
        for k, v in _type_readers.items():
            ext = v['extension']
            ext_bz2 = ext + '.bz2'
            if file_path.endswith(ext) or file_path.endswith(ext_bz2):
                file_type = k
                break

        else:
            raise RuntimeError("Unable to determine basis set format of '{}'".format(file_path))
    else:
        file_type = file_type.lower()

    if file_type not in _type_readers:
        raise RuntimeError("Unknown file type to read '{}'".format(file_type))

    fname = os.path.basename(file_path)

    # Handle compressed files
    if file_path.endswith('.bz2'):
        with bz2.open(file_path, 'rt') as f:
            basis_lines = [l.strip() for l in f.readlines()]
    else:
        with open(file_path, 'r') as f:
            basis_lines = [l.strip() for l in f.readlines()]

    data = _type_readers[file_type]['reader'](basis_lines, fname)
    return _fix_uncontracted(data)

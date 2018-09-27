'''
Read a basis set file in a given format
'''

from .turbomole import read_turbomole
from .g94 import read_g94
from .nwchem import read_nwchem
from .gbasis import read_gbasis

_type_readers = {'turbomole': read_turbomole, 'gaussian94': read_g94, 'nwchem': read_nwchem, 'gbasis': read_gbasis}


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


def read_formatted_basis(filepath, file_type):

    file_type = file_type.lower()
    if file_type not in _type_readers:
        raise RuntimeError("Unknown file type to read '{}'".format(file_type))

    data = _type_readers[file_type](filepath)
    return _fix_uncontracted(data)

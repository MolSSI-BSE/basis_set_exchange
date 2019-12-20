'''
Conversion of basis sets to Gaussian format
'''

from .g94 import write_g94


def write_psi4(basis):
    '''Converts a basis set to Psi4 format

    Psi4 uses the same output as gaussian94, except
    that the first line must be cartesian/spherical,
    and it prefers to have a starting asterisks

    The cartesian/spherical line is added later, since it must
    be the first non-blank line.
    '''

    s = '****\n'
    s += write_g94(basis)
    return s

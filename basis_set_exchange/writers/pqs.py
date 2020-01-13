'''
Conversion of basis sets to PQS
'''

from .. import lut, manip, sort, printing
from .gamess_us import write_gamess_us_ecp_basis


def write_pqs_electron_basis(basis, electron_elements):
    s = ''

    for z in electron_elements:
        data = basis['elements'][z]

        el_sym = lut.element_sym_from_Z(z, normalize=True)
        s += 'FOR        ' + el_sym + "\n"

        for shell in data['electron_shells']:
            exponents = shell['exponents']
            coefficients = shell['coefficients']

            am = shell['angular_momentum']
            amchar = lut.amint_to_char(am, hij=True, use_L=True).upper()

            ncol = len(coefficients) + 1
            point_places = [4 + 8 * i + 15 * (i - 1) for i in range(1, ncol+1)]
            mat = printing.write_matrix([exponents, *coefficients], point_places)

            # Prepend the AM
            mat = amchar + mat[1:]
            s += mat

    return s


def write_pqs(basis):
    '''Converts the basis set to PQS
    '''

    s = ''

    basis = manip.make_general(basis, True)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if electron_elements:
        s += write_pqs_electron_basis(basis, electron_elements)

    # Write out ECP
    if ecp_elements:
        s += '\n\n'
        s += 'Effective core Potentials\n'
        s += '-------------------------\n'
        s += write_gamess_us_ecp_basis(basis, ecp_elements, ecp_block=False)

    return s

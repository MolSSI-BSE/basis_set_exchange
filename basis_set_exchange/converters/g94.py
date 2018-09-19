'''
Conversion of basis sets to Gaussian format
'''

from .. import lut
from .. import manip
from .common import write_matrix


def write_g94(basis):
    '''Converts a basis set to Gaussian format
    '''

    s = ''

    basis = manip.uncontract_general(basis)
    basis = manip.uncontract_spdf(basis, 1)
    basis = manip.sort_basis(basis)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['basis_set_elements'].items() if 'element_electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['basis_set_elements'].items() if 'element_ecp' in v]

    # Electron Basis
    if len(electron_elements) > 0:
        for z in electron_elements:
            data = basis['basis_set_elements'][z]

            sym = lut.element_sym_from_Z(z, True)
            s += '{}     0\n'.format(sym)

            for shell in data['element_electron_shells']:
                exponents = shell['shell_exponents']
                coefficients = shell['shell_coefficients']
                ncol = len(coefficients) + 1
                nprim = len(exponents)

                am = shell['shell_angular_momentum']
                amchar = lut.amint_to_char(am, hij=True).upper()
                s += '{}   {}   1.00\n'.format(amchar, nprim)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += write_matrix([exponents, *coefficients], point_places, convert_exp=True)

            s += '****\n'

    # Write out ECP
    if len(ecp_elements) > 0:
        for z in ecp_elements:
            data = basis['basis_set_elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            max_ecp_am = max([x['potential_angular_momentum'][0] for x in data['element_ecp']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['element_ecp'], key=lambda x: x['potential_angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '{}     0\n'.format(sym)
            s += '{}-ECP     {}     {}\n'.format(sym, max_ecp_am, data['element_ecp_electrons'])

            for pot in ecp_list:
                rexponents = pot['potential_r_exponents']
                gexponents = pot['potential_gaussian_exponents']
                coefficients = pot['potential_coefficients']
                nprim = len(rexponents)

                am = pot['potential_angular_momentum']
                amchar = lut.amint_to_char(am, hij=True)

                if am[0] == max_ecp_am:
                    s += '{} potential\n'.format(amchar)
                else:
                    s += '{}-{} potential\n'.format(amchar, max_ecp_amchar)

                s += '  ' + str(nprim) + '\n'

                point_places = [0, 9, 32]
                s += write_matrix([rexponents, gexponents, *coefficients], point_places, convert_exp=True)

    return s

'''
Conversion of basis sets to Gaussian format
'''

import os
from .. import lut
from .. import manip
from .common import *


def write_g94(header, basis):
    '''Converts a basis set to Gaussian format
    '''

    s = u'! ' + header + '\n'

    unc_basis = manip.uncontract_general(basis)

    # Elements for which we have electron unc_basis
    electron_elements = [k for k, v in unc_basis['basis_set_elements'].items() if 'element_electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in unc_basis['basis_set_elements'].items() if 'element_ecp' in v]

    # basis set starts with ****
    # then we will put **** after each element
    s += '****'

    # Electron Basis
    if len(electron_elements) > 0:
        for z in electron_elements:
            data = unc_basis['basis_set_elements'][z]

            s += '\n'
            sym = lut.element_sym_from_Z(z, True)
            s += '{}     0\n'.format(sym)

            for shell in data['element_electron_shells']:
                am = shell['shell_angular_momentum']
                amchar = lut.amint_to_char(am, hij=True)
                amchar = amchar.upper()

                exponents = shell['shell_exponents']
                coefficients = shell['shell_coefficients']
                nprim = len(exponents)
                ngen = len(coefficients)

                # padding for exponents
                exponent_pad = determine_leftpad(exponents, 8)

                # Split apart general contractions, except for SP, SPD, etc orbitals
                # (basis was already uncontracted above)
                s += '{}   {}   1.00\n'.format(amchar, nprim)

                for p in range(nprim):
                    line = ' ' * exponent_pad[p] + exponents[p]
                    for c in range(ngen):
                        desired_point = 8 + (c + 1) * 23  # determined from PNNL BSE
                        coeff_pad = determine_leftpad(coefficients[c], desired_point)
                        line += ' ' * (coeff_pad[p] - len(line)) + coefficients[c][p]
                    s += line + '\n'

            s += '****'

    # Write out ECP
    if len(ecp_elements) > 0:
        for z in ecp_elements:
            data = unc_basis['basis_set_elements'][z]

            s += '\n'
            sym = lut.element_sym_from_Z(z)
            sym = sym.upper()

            max_ecp_am = max([x['potential_angular_momentum'][0] for x in data['element_ecp']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

            s += '{}     0\n'.format(sym)
            s += '{}-ECP     {}     {}\n'.format(sym, max_ecp_am, data['element_ecp_electrons'])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['element_ecp'], key=lambda x: x['potential_angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            for pot in ecp_list:
                am = pot['potential_angular_momentum']
                amchar = lut.amint_to_char(am, hij=True)

                rexponents = pot['potential_r_exponents']
                gexponents = pot['potential_gaussian_exponents']
                coefficients = pot['potential_coefficients']
                nprim = len(rexponents)
                ngen = len(coefficients)

                # Title line
                if am[0] == max_ecp_am:
                    s += '{} potential\n'.format(amchar)
                else:
                    s += '{}-{} potential\n'.format(amchar, max_ecp_amchar)

                # Number of entries
                s += '  ' + str(nprim) + '\n'

                # padding for exponents
                gexponent_pad = determine_leftpad(gexponents, 9)

                # General contractions?
                for p in range(nprim):
                    line = str(rexponents[p]) + ' ' * (gexponent_pad[p] - 1) + gexponents[p]
                    for c in range(ngen):
                        desired_point = 9 + (c + 1) * 23  # determined from PNNL BSE
                        coeff_pad = determine_leftpad(coefficients[c], desired_point)
                        line += ' ' * (coeff_pad[p] - len(line)) + coefficients[c][p]
                    s += line + '\n'

    return s

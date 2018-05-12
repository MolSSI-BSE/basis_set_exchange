'''
Conversion of basis sets to NWChem format
'''

import os
from .. import lut
from .. import manip
from .common import *


def write_nwchem(header, basis):
    '''Converts a basis set to NWChem format
    '''

    s = u'# ' + header + '\n'

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['basis_set_elements'].items() if 'element_electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['basis_set_elements'].items() if 'element_ecp' in v]

    if len(electron_elements) > 0:
        # basis set starts with a string
        s += 'BASIS "ao basis" PRINT\n'

        # Electron Basis
        for z in electron_elements:
            data = basis['basis_set_elements'][z]

            sym = lut.element_sym_from_Z(z, True)

            s += '#BASIS SET: {}\n'.format(manip.contraction_string(data))

            for shell in data['element_electron_shells']:
                am = shell['shell_angular_momentum']
                amchar = lut.amint_to_char(am)
                amchar = amchar.upper()

                s += '{}    {}\n'.format(sym, amchar)

                exponents = shell['shell_exponents']
                coefficients = shell['shell_coefficients']
                nprim = len(exponents)
                ngen = len(coefficients)

                # padding for exponents
                exponent_pad = determine_leftpad(exponents, 8)

                for p in range(nprim):
                    line = ' ' * exponent_pad[p] + exponents[p]
                    for c in range(ngen):
                        desired_point = 8 + (c + 1) * 23  # determined from PNNL BSE
                        coeff_pad = determine_leftpad(coefficients[c], desired_point)
                        line += ' ' * (coeff_pad[p] - len(line)) + coefficients[c][p]
                    s += line + '\n'
        s += 'END\n'

    # Write out ECP
    if len(ecp_elements):
        s += '\n\nECP\n'

        for z in ecp_elements:
            data = basis['basis_set_elements'][z]

            sym = lut.element_sym_from_Z(z)
            sym = lut.normalize_element_symbol(sym)

            max_ecp_am = max([x['potential_angular_momentum'][0] for x in data['element_ecp']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am])

            s += '{} nelec {}\n'.format(sym, data['element_ecp_electrons'])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['element_ecp'], key=lambda x: x['potential_angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            for pot in ecp_list:
                am = pot['potential_angular_momentum']
                amchar = lut.amint_to_char(am)
                amchar = amchar.lower()

                rexponents = pot['potential_r_exponents']
                gexponents = pot['potential_gaussian_exponents']
                coefficients = pot['potential_coefficients']
                nprim = len(rexponents)
                ngen = len(coefficients)

                # Title line
                if am[0] == max_ecp_am:
                    s += '{} ul\n'.format(sym)
                else:
                    s += '{} {}\n'.format(sym, amchar.upper())

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

        s += 'END\n'

    return s

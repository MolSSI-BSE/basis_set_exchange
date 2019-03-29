'''
Conversion of basis sets to Gaussian format
'''

from .. import lut, manip, sort, printing


def write_g94(basis):
    '''Converts a basis set to Gaussian format
    '''

    s = ''

    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 1, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if len(electron_elements) > 0:
        for z in electron_elements:
            data = basis['elements'][z]

            sym = lut.element_sym_from_Z(z, True)
            s += '{}     0\n'.format(sym)

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                ncol = len(coefficients) + 1
                nprim = len(exponents)

                am = shell['angular_momentum']
                amchar = lut.amint_to_char(am, hij=True).upper()
                s += '{}   {}   1.00\n'.format(amchar, nprim)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=True)

            s += '****\n'

    # Write out ECP
    if len(ecp_elements) > 0:
        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '{}     0\n'.format(sym)
            s += '{}-ECP     {}     {}\n'.format(sym, max_ecp_am, data['ecp_electrons'])

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']
                nprim = len(rexponents)

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am, hij=True)

                if am[0] == max_ecp_am:
                    s += '{} potential\n'.format(amchar)
                else:
                    s += '{}-{} potential\n'.format(amchar, max_ecp_amchar)

                s += '  ' + str(nprim) + '\n'

                point_places = [0, 9, 32]
                s += printing.write_matrix([rexponents, gexponents, *coefficients], point_places, convert_exp=True)

    return s

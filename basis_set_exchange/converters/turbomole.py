'''
Conversion of basis sets to Turbomole format
'''

from .. import lut, manip, sort, printing


def write_turbomole(basis):
    '''Converts a basis set to Gaussian format
    '''

    s = '$basis\n'
    s += '*\n'

    # TM basis sets are completely uncontracted
    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 0, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if len(electron_elements) > 0:
        for z in electron_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, False)
            s += '{} {}\n'.format(sym, basis['name'])
            s += '*\n'

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                ncol = len(coefficients) + 1
                nprim = len(exponents)

                am = shell['angular_momentum']
                amchar = lut.amint_to_char(am, hij=True)
                s += '    {}   {}\n'.format(nprim, amchar)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=True)

            s += '*\n'

    # Write out ECP
    if len(ecp_elements) > 0:
        s += '$ecp\n'
        s += '*\n'
        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z)
            s += '{} {}-ecp\n'.format(sym, basis['name'])
            s += '*\n'

            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '  ncore = {}   lmax = {}\n'.format(data['ecp_electrons'], max_ecp_am)

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am, hij=True)

                if am[0] == max_ecp_am:
                    s += '{}\n'.format(amchar)
                else:
                    s += '{}-{}\n'.format(amchar, max_ecp_amchar)

                point_places = [9, 23, 32]
                s += printing.write_matrix([*coefficients, rexponents, gexponents], point_places, convert_exp=True)
            s += '*\n'

    s += '$end\n'
    return s

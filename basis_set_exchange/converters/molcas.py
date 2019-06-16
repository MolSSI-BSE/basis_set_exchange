'''
Conversion of basis sets to Molcas format
'''

from .. import lut, manip, printing, misc, sort


def write_molcas(basis):
    '''Converts a basis set to Molcas format
    '''

    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    s = ''

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    if len(electron_elements) > 0:
        # Electron Basis
        for z in electron_elements:
            data = basis['elements'][z]
            el_name = lut.element_name_from_Z(z).upper()
            s += '* {}  {}\n'.format(el_name, misc.contraction_string(data))
            s += ' Basis set\n'
            s += ' {}    / inline\n'.format(el_name)

            # Since we did make_general, max_am is the number of shells - 1
            max_am = len(data['electron_shells']) - 1
            s += '{:>7}   {}\n'.format(z + '.00', max_am)

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                nprim = len(exponents)
                ngen = len(coefficients)

                amchar = lut.amint_to_char(shell['angular_momentum']).upper()
                s += '* {}-type functions\n'.format(amchar)
                s += '{:>6}    {}\n'.format(nprim, ngen)

                s += printing.write_matrix([exponents], [17])

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ngen + 1)]
                s += printing.write_matrix(coefficients, point_places)

    # Write out ECP
    if len(ecp_elements) > 0:
        s += '\n\nECP\n'

        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, True)
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '{} nelec {}\n'.format(sym, data['ecp_electrons'])

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am).upper()

                if am[0] == max_ecp_am:
                    s += '{} ul\n'.format(sym)
                else:
                    s += '{} {}\n'.format(sym, amchar)

                point_places = [0, 10, 33]
                s += printing.write_matrix([rexponents, gexponents, *coefficients], point_places)

        s += 'END\n'

    return s

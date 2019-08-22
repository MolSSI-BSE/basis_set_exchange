'''
Conversion of basis sets to CRYSTAL format
'''

from .. import lut, manip, sort, misc, printing


def write_crystal(basis):
    '''Converts a basis set to CRYSTAL format
    '''

    # This format is quite ...interesting...
    # It is relatively well documented, so see the manual
    # However, it is very restrictive...

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
            nshell = len(data['electron_shells'])

            has_ecp = 'ecp_electrons' in data

            # Print out the info line
            if has_ecp:
                s += '{} {}\n'.format(int(z)+200, nshell)
            else:
                s += '{} {}\n'.format(z, nshell)

            if has_ecp:
                s += 'INPUT\n'
                m = 0
                m0 = sum(len(x['coefficients'][0]) for x in data['ecp_potentials'] if x['angular_momentum'] == [0])
                m1 = sum(len(x['coefficients'][0]) for x in data['ecp_potentials'] if x['angular_momentum'] == [1])
                m2 = sum(len(x['coefficients'][0]) for x in data['ecp_potentials'] if x['angular_momentum'] == [2])
                m3 = sum(len(x['coefficients'][0]) for x in data['ecp_potentials'] if x['angular_momentum'] == [3])
                m4 = sum(len(x['coefficients'][0]) for x in data['ecp_potentials'] if x['angular_momentum'] == [4])
                s += "{} {} {} {} {} {} {}\n".format(data['ecp_electrons'], m, m0, m1, m2, m3, m4)

                ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
                all_g_exponents = []
                all_r_exponents = []
                all_coefficients = []
                for pot in ecp_list:
                    all_g_exponents.extend(pot['gaussian_exponents'])
                    all_r_exponents.extend(pot['r_exponents'])
                    all_coefficients.extend(pot['coefficients'][0])

                point_places = [8 * i + 15 * (i-1) for i in range(1, 4)]
                s += printing.write_matrix([all_g_exponents, all_coefficients, all_r_exponents], point_places, convert_exp=True)
                    

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                nprim = len(exponents)

                am = shell['angular_momentum']
                if am == [0]:
                    lat = 0
                elif am == [0, 1]:
                    lat = 1
                else:
                    if len(am) > 1:
                        raise RuntimeError("spd (or higher) shell found. CRYSTAL cannot handle this")
                    lat = int(am[0])+1

                charge = "TODO"
                s += '0 {} {} {} 1.0\n'.format(lat, nprim, charge)

                ncol = len(am) + 1
                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=True)

    return s
    # Write out ECP
    if len(ecp_elements) > 0:
        s += '\n\nECP\n'
        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, normalize=True)
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

                point_places = [0, 9, 32]
                s += printing.write_matrix([rexponents, gexponents, *coefficients], point_places, convert_exp=False)

        s += 'END\n'
    return s

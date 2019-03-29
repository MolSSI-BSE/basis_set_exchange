'''
Conversion of basis sets to cfour format
'''

from .. import lut, manip, sort, printing


def write_cfour(basis):
    '''Converts a basis set to cfour
    '''

    # March 2019
    # Format determined from http://slater.chemie.uni-mainz.de/cfour/index.php?n=Main.NewFormatOfAnEntryInTheGENBASFile

    # Uncontract all, then make general
    basis = manip.uncontract_spdf(basis, 0, True)
    basis = sort.sort_basis(basis, False)
    basis = manip.make_general(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    s = '\n'

    if len(electron_elements) > 0:
        # Electron Basis
        for z in electron_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            nshell = len(data['electron_shells'])

            s += '{}:{}\n'.format(sym, basis['name'])
            s += basis['description'] + '\n'
            s += '\n'
            s += '{:>3}\n'.format(nshell)

            s_am = ''
            s_ngen = ''
            s_nprim = ''
            for sh in data['electron_shells']:
                s_am += '{:>5}'.format(sh['angular_momentum'][0])
                s_ngen += '{:>5}'.format(len(sh['coefficients']))
                s_nprim += '{:>5}'.format(len(sh['exponents']))

            s += s_am + '\n'
            s += s_ngen + '\n'
            s += s_nprim + '\n'
            s += '\n'

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                coefficients = list(map(list, zip(*coefficients)))

                s += '  '.join(exponents).replace("E", "D") + '\n\n'
                for c in coefficients:
                    s += '  '.join(c).replace("E", "D") + '\n'
                s += '\n'

    # Write out ECP
    if len(ecp_elements) > 0:
        s += '\n\n! Effective core Potentials\n'

        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am]).lower()

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '*\n'
            s += '{}:{}\n'.format(sym, basis['name'])
            s += '# ' + basis['description'] + '\n'
            s += '*\n'
            s += '    NCORE = {}    LMAX = {}\n'.format(data['ecp_electrons'], max_ecp_am)

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am).lower()

                if am[0] == max_ecp_am:
                    s += '{}\n'.format(amchar)
                else:
                    s += '{}-{}\n'.format(amchar, max_ecp_amchar)

                point_places = [6, 18, 25]
                s += printing.write_matrix([*coefficients, rexponents, gexponents], point_places)
                #for p in range(len(rexponents)):
                #    s += '{}  {}  {};\n'.format(gexponents[p], rexponents[p], coefficients[0][p])
            s += '*\n'
    return s

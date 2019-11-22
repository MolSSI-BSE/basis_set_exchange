'''
Conversion of basis sets to GAMESS-US
'''

from .. import lut, manip, sort, printing


def write_gamess_us_electron_basis(basis, electron_elements):
    # electronic part starts with $DATA
    s = '$DATA\n'

    for z in electron_elements:
        data = basis['elements'][z]

        el_name = lut.element_name_from_Z(z).upper()
        s += '\n' + el_name + "\n"

        for shell in data['electron_shells']:
            exponents = shell['exponents']
            coefficients = shell['coefficients']
            ncol = len(coefficients) + 2  #include index column
            nprim = len(exponents)

            am = shell['angular_momentum']
            amchar = lut.amint_to_char(am, hij=True, use_L=True).upper()
            s += '{}   {}\n'.format(amchar, nprim)

            # 1-based indexing
            idx_column = list(range(1, nprim + 1))
            point_places = [0] + [4 + 8 * i + 15 * (i - 1) for i in range(1, ncol)]
            s += printing.write_matrix([idx_column, exponents, *coefficients], point_places)

    s += "$END"
    return s


def write_gamess_us_ecp_basis(basis, ecp_elements, ecp_block=True):
    s = ""

    if ecp_block:
        s += "\n\n$ECP\n"

    for z in ecp_elements:
        data = basis['elements'][z]
        sym = lut.element_sym_from_Z(z).upper()
        max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
        max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

        # Sort lowest->highest, then put the highest at the beginning
        ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
        ecp_list.insert(0, ecp_list.pop())

        s += '{}-ECP GEN    {}    {}\n'.format(sym, data['ecp_electrons'], max_ecp_am)

        for pot in ecp_list:
            rexponents = pot['r_exponents']
            gexponents = pot['gaussian_exponents']
            coefficients = pot['coefficients']
            nprim = len(rexponents)

            am = pot['angular_momentum']
            amchar = lut.amint_to_char(am, hij=False)

            # Title line
            if am[0] == max_ecp_am:
                s += '{:<5} ----- {}-ul potential -----\n'.format(nprim, amchar)
            else:
                s += '{:<5} ----- {}-{} potential -----\n'.format(nprim, amchar, max_ecp_amchar)

            point_places = [8, 23, 32]
            s += printing.write_matrix([*coefficients, rexponents, gexponents], point_places)

    if ecp_block:
        s += "$END\n"
    return s


def write_gamess_us_common(basis, ecp_func):
    '''Converts the electronic basis to GAMESS-US, using a
       different function for ECP
    '''

    s = ''

    # Uncontract all but SP
    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 1, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if electron_elements:
        s += write_gamess_us_electron_basis(basis, electron_elements)

    # Write out ECP
    if ecp_elements:
        s += ecp_func(basis, ecp_elements)

    return s


def write_gamess_us(basis):
    '''Converts a basis set to GAMESS-US
    '''

    return write_gamess_us_common(basis, write_gamess_us_ecp_basis)

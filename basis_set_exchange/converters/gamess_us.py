'''
Conversion of basis sets to Gaussian format
'''

from .. import lut
from .. import manip
from .common import write_matrix


def write_gamess_us(basis):
    '''Converts a basis set to GAMESS-US
    '''

    s = ''

    # Uncontract all but SP
    basis = manip.uncontract_general(basis)
    basis = manip.uncontract_spdf(basis, 1)
    basis = manip.sort_basis(basis)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['basis_set_elements'].items() if 'element_electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['basis_set_elements'].items() if 'element_ecp' in v]

    # Electron Basis
    if len(electron_elements) > 0:
        # electronic part starts with $DATA
        s += '$DATA\n'

        for z in electron_elements:
            data = basis['basis_set_elements'][z]

            el_name = lut.element_name_from_Z(z).upper()
            s += '\n' + el_name + "\n"

            for shell in data['element_electron_shells']:
                exponents = shell['shell_exponents']
                coefficients = shell['shell_coefficients']
                ncol = len(coefficients) + 2  #include index column
                nprim = len(exponents)

                am = shell['shell_angular_momentum']
                amchar = lut.amint_to_char(am, hij=True, use_L=True).upper()
                s += '{}   {}\n'.format(amchar, nprim)

                # 1-based indexing
                idx_column = list(range(1, nprim + 1))
                point_places = [0] + [4 + 8 * i + 15 * (i - 1) for i in range(1, ncol)]
                s += write_matrix([idx_column, exponents, *coefficients], point_places)

        s += "$END"

    # Write out ECP
    if len(ecp_elements) > 0:
        s += "\n\n$ECP\n"

        for z in ecp_elements:
            data = basis['basis_set_elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            max_ecp_am = max([x['potential_angular_momentum'][0] for x in data['element_ecp']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['element_ecp'], key=lambda x: x['potential_angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '{}-ECP GEN    {}    {}\n'.format(sym, data['element_ecp_electrons'], max_ecp_am)

            for pot in ecp_list:
                rexponents = pot['potential_r_exponents']
                gexponents = pot['potential_gaussian_exponents']
                coefficients = pot['potential_coefficients']
                nprim = len(rexponents)

                am = pot['potential_angular_momentum']
                amchar = lut.amint_to_char(am, hij=False)

                # Title line
                if am[0] == max_ecp_am:
                    s += '{:<5} ----- {}-ul potential -----\n'.format(nprim, amchar)
                else:
                    s += '{:<5} ----- {}-{} potential -----\n'.format(nprim, amchar, max_ecp_amchar)

                point_places = [8, 23, 32]
                s += write_matrix([*coefficients, rexponents, gexponents], point_places)

        s += "$END\n"

    return s

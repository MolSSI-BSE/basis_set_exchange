'''
Conversion of basis sets to NWChem format
'''

from .. import lut
from .. import manip
from .common import write_matrix


def write_nwchem(basis):
    '''Converts a basis set to NWChem format
    '''

    # Uncontract all but SP
    basis = manip.uncontract_spdf(basis, 1)
    basis = manip.sort_basis(basis)

    s = ''

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
                exponents = shell['shell_exponents']
                coefficients = shell['shell_coefficients']
                ncol = len(coefficients) + 1

                am = shell['shell_angular_momentum']
                amchar = lut.amint_to_char(am).upper()
                s += '{}    {}\n'.format(sym, amchar)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += write_matrix([exponents, *coefficients], point_places)

        s += 'END\n'

    # Write out ECP
    if len(ecp_elements) > 0:
        s += '\n\nECP\n'

        for z in ecp_elements:
            data = basis['basis_set_elements'][z]
            sym = lut.element_sym_from_Z(z, True)
            max_ecp_am = max([x['potential_angular_momentum'][0] for x in data['element_ecp']])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['element_ecp'], key=lambda x: x['potential_angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '{} nelec {}\n'.format(sym, data['element_ecp_electrons'])

            for pot in ecp_list:
                rexponents = pot['potential_r_exponents']
                gexponents = pot['potential_gaussian_exponents']
                coefficients = pot['potential_coefficients']

                am = pot['potential_angular_momentum']
                amchar = lut.amint_to_char(am).upper()

                if am[0] == max_ecp_am:
                    s += '{} ul\n'.format(sym)
                else:
                    s += '{} {}\n'.format(sym, amchar)

                point_places = [0, 10, 33]
                s += write_matrix([rexponents, gexponents, *coefficients], point_places)

        s += 'END\n'

    return s

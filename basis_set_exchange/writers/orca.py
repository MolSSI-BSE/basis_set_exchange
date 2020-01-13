'''
Conversion of basis sets to ORCA
'''

from .. import lut, printing
from .gamess_us import write_gamess_us_common


def write_orca_ecp_basis(basis, ecp_elements):
    s = ''
    for z in ecp_elements:
        s += '\n\n'
        data = basis['elements'][z]
        sym = lut.element_sym_from_Z(z).upper()
        max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
        max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

        # Sort lowest->highest
        ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])

        # Could probably be basis['names'][0]-ECP, but seems like special characters
        # would cause problems
        ecp_name = 'NewECP'
        s += '{} {}\n'.format(ecp_name, sym)
        s += '  N_core {}\n'.format(data['ecp_electrons'])
        s += '  lmax {}\n'.format(max_ecp_amchar)

        for pot in ecp_list:
            rexponents = pot['r_exponents']
            gexponents = pot['gaussian_exponents']
            coefficients = pot['coefficients']
            nprim = len(rexponents)

            am = pot['angular_momentum']
            amchar = lut.amint_to_char(am, hij=False)

            # Title line
            s += '  {} {}\n'.format(amchar, nprim)

            # Include an index column
            idx_column = list(range(1, nprim + 1))
            point_places = [4, 12, 27, 36]
            s += printing.write_matrix([idx_column, gexponents, *coefficients, rexponents], point_places)

        s += "end"
    return s


def write_orca(basis):
    '''Converts a basis set to ORCA
    '''

    return write_gamess_us_common(basis, write_orca_ecp_basis)

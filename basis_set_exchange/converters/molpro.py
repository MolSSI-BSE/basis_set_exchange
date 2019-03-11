'''
Conversion of basis sets to Molpro format
'''

from .. import lut
from .. import manip


def _find_range(coeffs):
    '''
    Find the range in a list of coefficients where the coefficient is nonzero
    '''

    coeffs = [float(x) != 0 for x in coeffs]
    first = coeffs.index(True)
    coeffs.reverse()
    last = len(coeffs) - coeffs.index(True) - 1
    return first, last


def write_molpro(basis):
    '''Converts a basis set to Molpro format
    '''

    # Uncontract all but SP
    basis = manip.uncontract_spdf(basis, 0)
    basis = manip.make_general(basis)

    s = ''

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    if len(electron_elements) > 0:
        # basis set starts with a string
        s += 'basis={\n'

        # Electron Basis
        for z in electron_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            s += '!\n'
            s += '! {:20} {}\n'.format(lut.element_name_from_Z(z), manip.contraction_string(data))

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']

                am = shell['angular_momentum']
                amchar = lut.amint_to_char(am).lower()
                s += '{}, {} , {}\n'.format(amchar, sym, ', '.join(exponents))
                for c in coefficients:
                    first, last = _find_range(c)
                    s += 'c, {}.{}, {}\n'.format(first + 1, last + 1, ', '.join(c[first:last + 1]))
        s += '}\n'

    # Write out ECP
    if len(ecp_elements) > 0:
        s += '\n\n! Effective core Potentials\n'

        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).lower()
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += 'ECP, {}, {}, {} ;\n'.format(sym, data['element_ecp_electrons'], max_ecp_am)

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am).lower()
                s += '{};'.format(len(rexponents))

                if am[0] == max_ecp_am:
                    s += ' !  ul potential\n'
                else:
                    s += ' !  {}-ul potential\n'.format(amchar)

                for p in range(len(rexponents)):
                    s += '{},{},{};\n'.format(rexponents[p], gexponents[p], coefficients[0][p])
    return s

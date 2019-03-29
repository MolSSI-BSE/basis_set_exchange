'''
Helpers for printing pieces of basis sets
'''

from . import lut
from .misc import expand_elements, contraction_string


def _find_point(x):
    if isinstance(x, int):
        return 0
    else:
        return x.index('.')


def _determine_leftpad(column, point_place):
    '''Find how many spaces to put before a column of numbers
       so that all the decimal points line up

    This function takes a column of decimal numbers, and returns a
    vector containing the number of spaces to place before each number
    so that (when possible) the decimal points line up.


    Parameters
    ----------
    column : list
        Numbers that will be printed as a column
    point_place : int
        Number of the character column to put the decimal point
    '''

    # Find the number of digits before the decimal
    ndigits_left = [_find_point(x) for x in column]

    # find the padding per entry, filtering negative numbers
    return [max((point_place - 1) - x, 0) for x in ndigits_left]


def write_matrix(mat, point_place, convert_exp=False):

    # Padding for the whole matrix
    pad = [_determine_leftpad(c, point_place[i]) for i, c in enumerate(mat)]

    # Use the transposes (easier to write out by row)
    pad = list(map(list, zip(*pad)))
    mat = list(map(list, zip(*mat)))

    lines = ''
    for r, row in enumerate(mat):
        line = ''
        for c, val in enumerate(row):
            sp = pad[r][c] - len(line)
            # ensure at least one space
            sp = max(sp, 1)
            line += ' ' * sp + str(mat[r][c])
        lines += line + '\n'

    if convert_exp is True:
        lines = lines.replace('e', 'D')
        lines = lines.replace('E', 'D')

    return lines


def electron_shell_str(shell, shellidx=None):
    '''Return a string representing the data for an electron shell

    If shellidx (index of the shell) is not None, it will also be printed
    '''
    am = shell['angular_momentum']
    amchar = lut.amint_to_char(am)
    amchar = amchar.upper()

    shellidx_str = ''
    if shellidx is not None:
        shellidx_str = 'Index {} '.format(shellidx)

    exponents = shell['exponents']
    coefficients = shell['coefficients']
    ncol = len(coefficients) + 1

    point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
    s = "Shell: {}Region: {}: AM: {}\n".format(shellidx_str, shell['region'], amchar)
    s += "Function: {} Harmonic: {}\n".format(shell['function_type'], shell['harmonic_type'])
    s += write_matrix([exponents, *coefficients], point_places)
    return s


def ecp_pot_str(pot):
    '''Return a string representing the data for an ECP potential
    '''

    am = pot['angular_momentum']
    amchar = lut.amint_to_char(am)

    rexponents = pot['r_exponents']
    gexponents = pot['gaussian_exponents']
    coefficients = pot['coefficients']

    point_places = [0, 10, 33]
    s = 'Potential: {} potential\n'.format(amchar)
    s += 'Type: {}\n'.format(pot['ecp_type'])
    s += write_matrix([rexponents, gexponents, *coefficients], point_places)
    return s


def element_data_str(z, eldata):
    '''Return a string with all data for an element

    This includes shell and ECP potential data

    Parameters
    ----------
    z : int or str
        Element Z-number
    eldata: dict
        Data for the element to be printed
    '''

    sym = lut.element_sym_from_Z(z, True)

    cs = contraction_string(eldata)
    if cs == '':
        cs = '(no electron shells)'
    s = '\nElement: {} : {}\n'.format(sym, cs)

    if 'electron_shells' in eldata:
        for shellidx, shell in enumerate(eldata['electron_shells']):
            s += electron_shell_str(shell, shellidx) + '\n'

    if 'ecp_potentials' in eldata:
        s += 'ECP: Element: {}   Number of electrons: {}\n'.format(sym, eldata['ecp_electrons'])

        for pot in eldata['ecp_potentials']:
            s += ecp_pot_str(pot) + '\n'

    return s


def component_basis_str(basis, elements=None):
    '''Print a component basis set

    If elements is not None, only the specified elements will be printed
    (see :func:`bse.misc.expand_elements`)
    '''

    s = "Description: " + basis['description'] + '\n'

    eldata = basis['elements']

    # Filter to the given elements
    if elements is None:
        elements = list(eldata.keys())
    else:
        elements = expand_elements(elements, True)

    # Add the str for each element
    for z in elements:
        s += element_data_str(z, eldata[z]) + '\n'

    return s

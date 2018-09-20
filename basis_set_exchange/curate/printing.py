'''
Helpers for printing pieces of basis sets
'''

from .. import lut
from .. import manip
from ..converters.common import write_matrix


def print_electron_shell(shell, shellidx=None):
    '''Print the data for an electron shell

    If shellidx (index of the shell) is not None, it will also be printed
    '''
    am = shell['shell_angular_momentum']
    amchar = lut.amint_to_char(am)
    amchar = amchar.upper()

    if shellidx is not None:
        shellidx = ''

    exponents = shell['shell_exponents']
    coefficients = shell['shell_coefficients']
    ncol = len(coefficients) + 1

    point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
    print("Shell {} '{}': AM {} ({})".format(shellidx, shell['shell_region'], am, amchar))
    print(write_matrix([exponents, *coefficients], point_places))


def print_ecp_pot(pot):
    '''Print the data for an ECP potential
    '''

    am = pot['potential_angular_momentum']
    amchar = lut.amint_to_char(am)

    rexponents = pot['potential_r_exponents']
    gexponents = pot['potential_gaussian_exponents']
    coefficients = pot['potential_coefficients']

    point_places = [0, 10, 33]
    print('Potential: {} potential'.format(amchar))
    print(write_matrix([rexponents, gexponents, *coefficients], point_places))


def print_element(z, eldata, print_references=True):
    '''Print all data for an element

    Parameters
    ----------
    z : integer
        Element Z-number
    eldata:
        Data for the element to be printed
    '''

    sym = lut.element_sym_from_Z(z, True)

    print()
    print('Element: {}   Contraction: {}'.format(sym, manip.contraction_string(eldata)))
    if print_references:
        if 'element_references' in eldata:
            print('References:')
            for x in eldata['element_references']:
                print('    ' + ', '.join(x['reference_keys']))
                print('        ' + x['reference_description'])
        else:
            print('References: NONE')

    if 'element_electron_shells' in eldata:
        for shellidx, shell in enumerate(eldata['element_electron_shells']):
            print_electron_shell(shell, shellidx)

    if 'element_ecp' in eldata:
        print('ECP: Element: {}   Number of electrons: {}'.format(sym, eldata['element_ecp_electrons']))

        # Sort lowest->highest, then put the highest at the beginning
        ecp_list = sorted(eldata['element_ecp'], key=lambda x: x['potential_angular_momentum'])
        ecp_list.insert(0, ecp_list.pop())

        for pot in ecp_list:
            print_ecp_pot(pot)


def print_component_basis(basis, elements=None):
    '''Print a component basis set

    If elements is not None, only the specified elements will be printed
    (list of integers)
    '''
    print("Description: " + basis['basis_set_description'])
    print('References: ' + ', '.join(basis['basis_set_references']))

    eldata = basis['basis_set_elements']

    # Filter to the given elements
    if elements is None:
        elements = list(eldata.keys())
    else:
        elements = [k for k in eldata.keys() if k in elements]

    # Electron Basis
    for z in elements:
        print_element(z, eldata[z], False)


def print_element_basis(basis, elements=None):
    '''Print an element basis set

    If elements is not None, only the specified elements will be printed
    (list of integers)
    '''
    print("Basis set: " + basis['basis_set_name'])
    print("Description: " + basis['basis_set_description'])

    eldata = basis['basis_set_elements']

    if elements is None:
        elements = list(eldata.keys())
    else:
        elements = [k for k in eldata.keys() if k in elements]

    # strings
    complist = {z: eldata[z]['element_components'] for z in elements}

    # Header line
    print('{:4} {}'.format("El", "Components"))
    print('-' * 80)
    for z in elements:
        sym = lut.element_sym_from_Z(z, True)
        print('{:4} {}'.format(sym, complist[z][0]))
        for v in complist[z][1:]:
            print('{:4} {}'.format('', v))
    print()


def print_table_basis(basis, elements=None):
    '''Print a full table basis set

    If elements is not None, only the specified elements will be printed
    (list of integers)
    '''

    print("Basis set: " + basis['basis_set_name'])
    print("Description: " + basis['basis_set_description'])
    print("Role: " + basis['basis_set_role'])
    print()

    eldata = basis['basis_set_elements']

    if elements is None:
        elements = list(eldata.keys())
    else:
        elements = [k for k in eldata.keys() if k in elements]

    # strings
    complist = {z: eldata[z]['element_entry'] for z in elements}

    # Header line
    print('{:4} {}'.format("El", "Entry"))
    print('-' * 80)
    for z in elements:
        sym = lut.element_sym_from_Z(z, True)
        print('{:4} {}'.format(sym, complist[z]))

    print()

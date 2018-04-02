from .. import lut
from .. import manip
from ..converters.common import *


def print_shell(shell, shellidx=None):
    am = shell['shell_angular_momentum']
    amchar = lut.amint_to_char(am)
    amchar = amchar.upper()

    if shellidx is not None:
        shellidx = ''

    print("Shell {} '{}': AM {} ({})".format(shellidx, shell['shell_region'], am, amchar))

    exponents = shell['shell_exponents']
    coefficients = shell['shell_coefficients']
    nprim = len(exponents)
    ngen = len(coefficients)

    # padding for exponents
    exponent_pad = determine_leftpad(exponents, 8)

    for p in range(nprim):
        line = ' ' * exponent_pad[p] + exponents[p]
        for c in range(ngen):
            desired_point = 8 + (c + 1) * 23  # determined from PNNL BSE
            coeff_pad = determine_leftpad(coefficients[c], desired_point)
            line += ' ' * (coeff_pad[p] - len(line)) + coefficients[c][p]
        print(line)


def print_ecp_pot(pot):
    am = pot['potential_angular_momentum']
    amchar = lut.amint_to_char(am)

    rexponents = pot['potential_r_exponents']
    gexponents = pot['potential_gaussian_exponents']
    coefficients = pot['potential_coefficients']
    nprim = len(rexponents)
    ngen = len(coefficients)

    # Title line
    print('Potential: {} potential'.format(amchar))

    # padding for exponents
    gexponent_pad = determine_leftpad(gexponents, 9)

    # General contractions?
    for p in range(nprim):
        line = str(rexponents[p]) + ' ' * (gexponent_pad[p] - 1) + gexponents[p]
        for c in range(ngen):
            desired_point = 9 + (c + 1) * 23  # determined from PNNL BSE
            coeff_pad = determine_leftpad(coefficients[c], desired_point)
            line += ' ' * (coeff_pad[p] - len(line)) + coefficients[c][p]
        print(line)


def print_element(z, eldata):
    sym = lut.element_sym_from_Z(z)
    sym = lut.normalize_element_symbol(sym, True)

    print()
    print('Element: {}   Contraction: {}'.format(sym, manip.contraction_string(eldata)))
    if 'element_references' in eldata:
        print('References: {}'.format(' '.join(eldata['element_references'])))
    else:
        print('References: NONE')

    if 'element_electron_shells' in eldata:
        for shellidx, shell in enumerate(eldata['element_electron_shells']):
            print_shell(shell, shellidx)

    if 'element_ecp' in eldata:
        max_ecp_am = max([x['potential_angular_momentum'][0] for x in eldata['element_ecp']])
        max_ecp_amchar = lut.amint_to_char([max_ecp_am])

        print('ECP: Element: {}   Number of electrons: {}'.format(sym, eldata['element_ecp_electrons']))

        # Sort lowest->highest, then put the highest at the beginning
        ecp_list = sorted(eldata['element_ecp'], key=lambda x: x['potential_angular_momentum'])
        ecp_list.insert(0, ecp_list.pop())

        for pot in ecp_list:
            print_ecp_pot(pot)


def print_component_basis(basis, elements=None):
    print("Basis set: " + basis['basis_set_name'])
    print("Description: " + basis['basis_set_description'])
    eldata = basis['basis_set_elements']

    # Filter to the given elements
    if elements is None:
        elements = list(eldata.keys())
    else:
        elements = [k for k in eldata.keys() if k in elements]

    # Electron Basis
    for z in elements:
        print_element(z, eldata[z])


def print_element_basis(basis, elements=None):
    print("Basis set: " + basis['basis_set_name'])
    print("Description: " + basis['basis_set_description'])

    eldata = basis['basis_set_elements']

    if elements is None:
        elements = list(eldata.keys())
    else:
        elements = [k for k in eldata.keys() if k in elements]

    # strings
    complist = {z: ' '.join(eldata[z]['element_components']) for z in elements}
    reflist = {z: ' '.join(eldata[z]['element_references']) for z in elements if 'element_references' in eldata[z]}

    max_comp = max([len(x) for k, x in complist.items()])
    max_comp = max(max_comp, len("Components"))

    # Header line
    print('{:4} {:{}} {:20}'.format("El", "Components", max_comp + 1, "References"))
    print('-' * 80)
    for z in elements:
        data = basis['basis_set_elements'][z]

        sym = lut.element_sym_from_Z(z)
        sym = lut.normalize_element_symbol(sym)

        print('{:4} {:{}} {:20}'.format(sym, complist[z], max_comp + 1, reflist[z] if z in reflist else 'None'))

    print()


def print_table_basis(basis, elements=None):
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
    reflist = {z: eldata[z]['element_references'] for z in elements if 'element_references' in eldata[z]}

    max_comp = max([len(x) for k, x in complist.items()])
    max_comp = max(max_comp, len("Components"))

    # Header line
    print('{:4} {:{}} {:20}'.format("El", "Entry", max_comp + 1, "References"))
    print('-' * 80)
    for z in elements:
        data = basis['basis_set_elements'][z]

        sym = lut.element_sym_from_Z(z)
        sym = lut.normalize_element_symbol(sym)

        print('{:4} {:{}} {:20}'.format(sym, complist[z], max_comp + 1, reflist[z] if z in reflist else 'None'))

    print()


def print_citation(citkey, cit):
    print("Citation: {}".format(citkey))

    doistr = cit['DOI'] if 'DOI' in cit else 'MISSING'
    print("    DOI: {}".format(doistr))

    titlestr = cit['title'] if 'title' in cit else 'MISSING'
    print("    Title: {}".format(titlestr))

    if 'authors' in cit and len(cit['authors']) > 0:
        print("    Authors: {}".format(cit['authors'][0]))
        for a in cit['authors'][1:]:
            print("             {}".format(a))
    else:
        print("    Authors: NONE")

    journalstr = cit['journal'] if 'journal' in cit else "MISSING"
    volumestr = cit['volume'] if 'volume' in cit else "MISSING"
    pagestr = cit['page'] if 'page' in cit else "MISSING"
    yearstr = cit['year'] if 'year' in cit else "MISSING"

    print("    {} v{} pp {} ({})".format(journalstr, volumestr, pagestr, yearstr))

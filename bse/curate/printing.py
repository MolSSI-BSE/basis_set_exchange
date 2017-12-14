from .. import lut
from .. import manip
from ..converters.common import *

def print_shell(shell, shellidx=None):
    am = shell['shellAngularMomentum']
    amchar = lut.amint_to_char(am)
    amchar = amchar.upper()

    if shellidx is not None:
        shellidx = ''

    print("Shell {} '{}': AM {} ({})".format(shellidx, shell['shellRegion'], am, amchar))

    exponents = shell['shellExponents']
    coefficients = shell['shellCoefficients']
    nprim = len(exponents)
    ngen = len(coefficients)

    # padding for exponents
    exponent_pad = determine_leftpad(exponents, 8)

    for p in range(nprim):
        line = ' '*exponent_pad[p] + exponents[p]
        for c in range(ngen):
            desired_point = 8 + (c+1)*23  # determined from PNNL BSE
            coeff_pad = determine_leftpad(coefficients[c], desired_point)
            line += ' '*(coeff_pad[p] - len(line)) + coefficients[c][p]
        print(line)


def print_ecp_pot(pot):
    am = pot['potentialAngularMomentum']
    amchar = lut.amint_to_char(am)

    rexponents = pot['potentialRExponents']
    gexponents = pot['potentialGaussianExponents']
    coefficients = pot['potentialCoefficients']
    nprim = len(rexponents)
    ngen = len(coefficients)


    # Title line
    print('Potential: {} potential'.format(amchar))

    # padding for exponents
    gexponent_pad = determine_leftpad(gexponents, 9)

    # General contractions?
    for p in range(nprim):
        line = str(rexponents[p]) + ' '*(gexponent_pad[p]-1) + gexponents[p]
        for c in range(ngen):
            desired_point = 9 + (c+1)*23  # determined from PNNL BSE
            coeff_pad = determine_leftpad(coefficients[c], desired_point)
            line += ' '*(coeff_pad[p] - len(line)) + coefficients[c][p]
        print(line)


def print_element(z, eldata):
    sym = lut.element_sym_from_Z(z)
    sym = lut.normalize_element_symbol(sym)

    print()
    print('Element: {}   Contraction: {}'.format(sym, manip.contraction_string(eldata)))
    if 'elementReferences' in eldata:
        print('References: {}'.format(' '.join(eldata['elementReferences'])))
    else:
        print('References: NONE')

    if 'elementElectronShells' in eldata:
        for shellidx,shell in enumerate(eldata['elementElectronShells']):
            print_shell(shell, shellidx)

    if 'elementECP' in eldata:
        max_ecp_am = max([ x['potentialAngularMomentum'][0] for x in eldata['elementECP'] ])
        max_ecp_amchar = lut.amint_to_char([max_ecp_am])

        print('ECP: Element: {}   Number of electrons: {}'.format(sym, eldata['elementECPElectrons']))

        # Sort lowest->highest, then put the highest at the beginning
        ecp_list = sorted(eldata['elementECP'], key=lambda x: x['potentialAngularMomentum'])
        ecp_list.insert(0, ecp_list.pop())

        for pot in ecp_list:
            print_ecp_pot(pot)


def print_component_basis(basis, elements=None):
    print("Basis set: " + basis['basisSetName'])
    print("Description: " + basis['basisSetDescription'])
    eldata = basis['basisSetElements']

    # Filter to the given elements
    if elements is not None:
        elements = [ k for k, v in eldata.items() if k in elements ]

    # Electron Basis
    for z in elements:
        print_element(z, eldata[z])


def print_element_basis(basis, elements=None):
    print("Basis set: " + basis['basisSetName'])
    print("Description: " + basis['basisSetDescription'])

    eldata = basis['basisSetElements']

    if elements is not None:
        elements = [ k for k, v in eldata.items() if k in elements ]

    # strings
    complist = { z: ' '.join(eldata[z]['elementComponents']) for z in elements }
    reflist = { z: ' '.join(eldata[z]['elementReferences']) for z in elements if 'elementReferences' in eldata[z]}

    max_comp = max( [ len(x) for k,x in complist.items() ] )
    max_comp = max(max_comp, len("Components"))

    # Header line
    print('{:4} {:{}} {:20}'.format("El", "Components", max_comp+1, "References"))
    print('-'*80)
    for z in elements:
        data = basis['basisSetElements'][z]

        sym = lut.element_sym_from_Z(z)
        sym = lut.normalize_element_symbol(sym)

        print('{:4} {:{}} {:20}'.format(sym, complist[z], max_comp+1, reflist[z] if z in reflist else 'None'))

    print()


def print_table_basis(basis, elements=None):
    print("Basis set: " + basis['basisSetName'])
    print("Description: " + basis['basisSetDescription'])
    print("Role: " + basis['basisSetRole'])
    print()

    eldata = basis['basisSetElements']

    if elements is not None:
        elements = [ k for k, v in eldata.items() if k in elements ]

    # strings
    complist = { z: eldata[z]['elementEntry'] for z in elements }
    reflist = { z: eldata[z]['elementReferences'] for z in elements if 'elementReferences' in eldata[z]}

    max_comp = max( [ len(x) for k,x in complist.items() ] )
    max_comp = max(max_comp, len("Components"))

    # Header line
    print('{:4} {:{}} {:20}'.format("El", "Entry", max_comp+1, "References"))
    print('-'*80)
    for z in elements:
        data = basis['basisSetElements'][z]

        sym = lut.element_sym_from_Z(z)
        sym = lut.normalize_element_symbol(sym)

        print('{:4} {:{}} {:20}'.format(sym, complist[z], max_comp+1, reflist[z] if z in reflist else 'None'))

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


import os
from .. import lut
from .. import manip
from .common import *


def write_nwchem(basis):
    s = u'# NWChem Basis set: ' + basis['basisSetName'] + '\n'

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['basisSetElements'].items() if 'elementElectronShells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['basisSetElements'].items() if 'elementECP' in v]

    # basis set starts with a string
    s += 'BASIS "ao basis" PRINT\n'

    # Electron Basis
    for z in electron_elements:
        data = basis['basisSetElements'][z]

        sym = lut.element_sym_from_Z(z, True)

        s += '# BASIS SET: {}\n'.format(manip.contraction_string(data))

        for shell in data['elementElectronShells']:
            am = shell['shellAngularMomentum']
            amchar = lut.amint_to_char(am)
            amchar = amchar.upper()

            s += '{}    {}\n'.format(sym, amchar)

            exponents = shell['shellExponents']
            coefficients = shell['shellCoefficients']
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
                s += line + '\n'
    s += 'END\n'

    # Write out ECP
    if len(ecp_elements):
        s += '\n\nECP\n'

    for z in ecp_elements:
        data = basis['basisSetElements'][z]

        sym = lut.element_sym_from_Z(z)
        sym = lut.normalize_element_symbol(sym)

        max_ecp_am = max([x['potentialAngularMomentum'][0] for x in data['elementECP']])
        max_ecp_amchar = lut.amint_to_char([max_ecp_am])

        s += '{} nelec {}\n'.format(sym, data['elementECPElectrons'])

        # Sort lowest->highest, then put the highest at the beginning
        ecp_list = sorted(data['elementECP'], key=lambda x: x['potentialAngularMomentum'])
        ecp_list.insert(0, ecp_list.pop())

        for pot in ecp_list:
            am = pot['potentialAngularMomentum']
            amchar = lut.amint_to_char(am)
            amchar = amchar.lower()

            rexponents = pot['potentialRExponents']
            gexponents = pot['potentialGaussianExponents']
            coefficients = pot['potentialCoefficients']
            nprim = len(rexponents)
            ngen = len(coefficients)

            # Title line
            if am[0] == max_ecp_am:
                s += '{} {} potential\n'.format(sym, amchar)
            else:
                s += '{} {}-{} potential\n'.format(sym, amchar, max_ecp_amchar)

            # padding for exponents
            gexponent_pad = determine_leftpad(gexponents, 9)

            # General contractions?
            for p in range(nprim):
                line = str(rexponents[p]) + ' ' * (gexponent_pad[p] - 1) + gexponents[p]
                for c in range(ngen):
                    desired_point = 9 + (c + 1) * 23  # determined from PNNL BSE
                    coeff_pad = determine_leftpad(coefficients[c], desired_point)
                    line += ' ' * (coeff_pad[p] - len(line)) + coefficients[c][p]
                s += line + '\n'

    if len(ecp_elements):
        s += 'END\n'

    return s

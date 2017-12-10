import os
from .. import lut
from .. import manip

skipchars = '!'

def determine_leftpad(column, desired_place):
    # Find the number of digits before the decimal
    ndigits_left = [ x.index('.') for x in column ]

    # Maximum number of digits
    # ndigits_left_max = max(ndigits_left)

    # find the padding per entry, filtering negative numbers
    padding = [ max((desired_place - 1) - x, 0) for x in ndigits_left ]

    return padding
    

def write_g94(basis):
    s = "! G94 Basis set: " + basis['basisSetName'] + '\n'

    unc_basis = manip.uncontract_general(basis)

    # Elements for which we have electron unc_basis
    electron_elements = [ k for k, v in unc_basis['basisSetElements'].items() if 'elementElectronShells' in v ]

    # Elements for which we have ECP
    ecp_elements = [ k for k, v in unc_basis['basisSetElements'].items() if 'elementECP' in v ]

    # basis set starts with ****
    # then we will put **** after each element
    s += '****'

    # Electron Basis
    for z in electron_elements:
        data = unc_basis['basisSetElements'][z]

        s += '\n'
        sym = lut.element_sym_from_Z(z)
        sym = lut.normalize_element_symbol(sym)
        s += '{}     0\n'.format(sym)

        for shell in data['elementElectronShells']:
            am = shell['shellAngularMomentum']
            amchar = lut.amint_to_char(am)
            amchar = amchar.upper()

            exponents = shell['shellExponents']
            coefficients = shell['shellCoefficients']
            nprim = len(exponents)
            ngen = len(coefficients)

            # padding for exponents
            exponent_pad = determine_leftpad(exponents, 8)

            # Split apart general contractions, except for SP, SPD, etc orbitals
            # (basis was already uncontracted above)
            s += '{}   {}   1.00\n'.format(amchar, nprim)

            for p in range(nprim):
                line = ' '*exponent_pad[p] + exponents[p]
                for c in range(ngen):
                    desired_point = 8 + (c+1)*23  # determined from PNNL BSE
                    coeff_pad = determine_leftpad(coefficients[c], desired_point)
                    line += ' '*(coeff_pad[p] - len(line)) + coefficients[c][p]
                s += line + '\n'

        s += '****'


    # Write out ECP
    for z in ecp_elements:
        data = unc_basis['basisSetElements'][z]

        s += '\n'
        sym = lut.element_sym_from_Z(z)
        sym = sym.upper()


        max_ecp_am = max([ x['potentialAngularMomentum'][0] for x in data['elementECP'] ])
        max_ecp_amchar = lut.amint_to_char([max_ecp_am])

        s += '{}     0\n'.format(sym)
        s += '{}-ECP     {}     {}\n'.format(sym, max_ecp_am, data['elementECPElectrons'])

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
                s += '{} potential\n'.format(amchar)
            else:
                s += '{}-{} potential\n'.format(amchar, max_ecp_amchar)

            # Number of entries
            s += '  ' + str(nprim) + '\n'

            # padding for exponents
            gexponent_pad = determine_leftpad(gexponents, 9)

            # General contractions?
            for p in range(nprim):
                line = str(rexponents[p]) + ' '*(gexponent_pad[p]-1) + gexponents[p]
                for c in range(ngen):
                    desired_point = 9 + (c+1)*23  # determined from PNNL BSE
                    coeff_pad = determine_leftpad(coefficients[c], desired_point)
                    line += ' '*(coeff_pad[p] - len(line)) + coefficients[c][p]
                s += line + '\n'

    return s

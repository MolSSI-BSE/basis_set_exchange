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
    

def g94_to_json(basis_name, basis_path):
    if not os.path.isfile(basis_path):
        raise RuntimeError('G94 basis set path \'{}\' does not exist'.format(basis_path))

    with open(basis_path, 'r') as f:
        basis_lines = [l.strip() for l in f]
        basis_lines = [l for l in basis_lines if l and not l[0] in skipchars]

    js_data = {'name': basis_name, 'harmonic': 'cartesian', 'elements': {}}

    i = 1  # skip initial ****
    while i < len(basis_lines):
        line = basis_lines[i]
        elementsym = line.split()[0]
        element_Z = lut.element_data_from_sym(elementsym)[0]

        element_data = {'electronShells': {'valence': {'version': "1.0", 'shells': []}}}

        i += 1
        if "ECP" in basis_lines[i]:
            maxam = int(lsplt[1])
            n_elec = int(lsplt[2])

            i += 1
            for j in range(maxam + 1):
                shell_am = lut.amchar_to_int(basis_lines[i][0])[0]
                i += 1
                n_entries = int(basis_lines[i])
                i += 1

                ecp_shell = {'angularMomentum': shell_am}
                ecp_exponents = []
                ecp_coefficients = []

                for k in range(n_entries):
                    lsplt = basis_lines[i].split()
                    exp_exponents.append(lsplt[0])
                    exp_coefficients.append(lsplt[1])
                    i += 1

                js_data['elements'][element_Z]['ecp'].append(ecp_shell)
        else:
            while basis_lines[i] != '****':
                lsplt = basis_lines[i].split()
                shell_am = lut.amchar_to_int(lsplt[0])
                nshell = int(lsplt[1])

                shell = {'angularMomentum': shell_am}
                exponents = []
                coefficients = []

                i += 1
                for j in range(nshell):
                    lsplt = basis_lines[i].split()
                    exponents.append(lsplt[0])
                    coefficients.append(lsplt[1:])
                    i += 1

                shell['exponents'] = exponents

                # We need to transpose the coefficient matrix
                # (we store a matrix with primitives being the column index and
                # general contraction being the row index)
                shell['coefficients'] = list(map(list, zip(*coefficients)))

                element_data['electronShells']['valence']['shells'].append(shell)
                js_data['elements'][element_Z] = element_data

        i += 1

    return js_data


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

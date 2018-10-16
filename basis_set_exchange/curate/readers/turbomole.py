from ... import lut


def read_turbomole(basis_lines, fname):
    '''Reads turbomole-formatted file data and converts it to a dictionary with the
       usual BSE fields

       Note that the turbomole format does not store all the fields we
       have, so some fields are left blank
    '''

    skipchars = '*#$'
    basis_lines = [l for l in basis_lines if l and not l[0] in skipchars]

    bs_data = {
        'molssi_bse_schema': {
            'schema_type': 'component',
            'schema_version': '0.1'
        },
        'basis_set_description': fname,
        'basis_set_references': [],
        'basis_set_elements': {}
    }

    i = 0
    while i < len(basis_lines):
        line = basis_lines[i]
        elementsym = line.split()[0]

        element_Z = lut.element_Z_from_sym(elementsym)
        element_Z = str(element_Z)

        if not element_Z in bs_data['basis_set_elements']:
            bs_data['basis_set_elements'][element_Z] = {}

        element_data = bs_data['basis_set_elements'][element_Z]

        if "ecp" in line.lower():
            if not 'element_ecp' in element_data:
                element_data['element_ecp'] = []

            i += 1
            line = basis_lines[i]

            lsplt = line.split('=')
            maxam = int(lsplt[2])
            n_elec = int(lsplt[1].split()[0])

            amlist = [maxam]
            amlist.extend(list(range(0, maxam)))

            i += 1
            for shell_am in amlist:
                shell_am2 = lut.amchar_to_int(basis_lines[i][0])[0]
                if shell_am2 != shell_am:
                    raise RuntimeError("AM not in expected order?")

                i += 1

                ecp_shell = {
                    'potential_ecp_type': 'scalar',
                    'potential_angular_momentum': [shell_am],
                }
                ecp_exponents = []
                ecp_rexponents = []
                ecp_coefficients = []

                while i < len(basis_lines) and basis_lines[i][0].isalpha() is False:
                    lsplt = basis_lines[i].split()
                    ecp_exponents.append(lsplt[2])
                    ecp_rexponents.append(int(lsplt[1]))
                    ecp_coefficients.append(lsplt[0])
                    i += 1

                ecp_shell['potential_r_exponents'] = ecp_rexponents
                ecp_shell['potential_gaussian_exponents'] = ecp_exponents
                ecp_shell['potential_coefficients'] = [ecp_coefficients]
                element_data['element_ecp'].append(ecp_shell)

            element_data['element_ecp_electrons'] = n_elec

        else:
            if not 'element_electron_shells' in element_data:
                element_data['element_electron_shells'] = []

            i += 1
            while i < len(basis_lines) and basis_lines[i][0].isalpha() == False:
                lsplt = basis_lines[i].split()
                shell_am = lut.amchar_to_int(lsplt[1])
                nprim = int(lsplt[0])

                shell = {
                    'shell_function_type': 'gto',
                    'shell_harmonic_type': 'spherical',
                    'shell_region': '',
                    'shell_angular_momentum': shell_am
                }

                exponents = []
                coefficients = []

                i += 1
                for j in range(nprim):
                    line = basis_lines[i].replace('D', 'E')
                    line = line.replace('d', 'E')
                    lsplt = line.split()
                    exponents.append(lsplt[0])
                    coefficients.append(lsplt[1:])
                    i += 1

                shell['shell_exponents'] = exponents

                # We need to transpose the coefficient matrix
                # (we store a matrix with primitives being the column index and
                # general contraction being the row index)
                shell['shell_coefficients'] = list(map(list, zip(*coefficients)))

                element_data['element_electron_shells'].append(shell)

    return bs_data

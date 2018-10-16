from ... import lut


def read_nwchem(basis_lines, fname):
    '''Reads NWChem-formatted file data and converts it to a dictionary with the
       usual BSE fields

       Note that the nwchem format does not store all the fields we
       have, so some fields are left blank
    '''

    skipchars = '#'
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

        if line.lower().startswith('basis'):
            i += 1

            # NWChem doesn't seem to really block by element
            # It just has shells labeled with each element symbol

            while i < len(basis_lines) and not basis_lines[i].lower().startswith('end'):
                line = basis_lines[i]
                lsplt = line.split()
                elementsym = lsplt[0]
                shell_am = lut.amchar_to_int(lsplt[1])

                element_Z = lut.element_Z_from_sym(elementsym)
                element_Z = str(element_Z)

                if not element_Z in bs_data['basis_set_elements']:
                    bs_data['basis_set_elements'][element_Z] = {}
                if not 'element_electron_shells' in bs_data['basis_set_elements'][element_Z]:
                    bs_data['basis_set_elements'][element_Z]['element_electron_shells'] = []

                element_data = bs_data['basis_set_elements'][element_Z]

                shell = {
                    'shell_function_type': 'gto',
                    'shell_harmonic_type': 'spherical',
                    'shell_region': 'valence',
                    'shell_angular_momentum': shell_am
                }

                exponents = []
                coefficients = []

                i += 1
                while True:
                    if i >= len(basis_lines) or basis_lines[i][0].isalpha():
                        break

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

        elif line.lower().startswith('ecp'):
            i += 1
            while i < len(basis_lines) and not basis_lines[i].lower().startswith('end'):
                line = basis_lines[i]
                if 'nelec' in line.lower():
                    lsplt = line.split()
                    elementsym = lsplt[0]
                    n_elec = int(lsplt[2])

                    element_Z = lut.element_Z_from_sym(elementsym)
                    element_Z = str(element_Z)

                    if not element_Z in bs_data['basis_set_elements']:
                        bs_data['basis_set_elements'][element_Z] = {}
                    if not 'element_ecp_electrons' in bs_data['basis_set_elements'][element_Z]:
                        bs_data['basis_set_elements'][element_Z]['element_ecp_electrons'] = n_elec

                    i += 1
                    continue

                # Now parsing a shell
                lsplt = line.split()
                elementsym = lsplt[0]

                shell_am = lsplt[1]
                if shell_am.lower() == 'ul':
                    shell_am = -1  # Placeholder - leave for later
                else:
                    shell_am = lut.amchar_to_int(lsplt[1])

                element_Z = lut.element_Z_from_sym(elementsym)
                element_Z = str(element_Z)

                if not element_Z in bs_data['basis_set_elements']:
                    bs_data['basis_set_elements'][element_Z] = {}
                if not 'element_ecp' in bs_data['basis_set_elements'][element_Z]:
                    bs_data['basis_set_elements'][element_Z]['element_ecp'] = []
                element_data = bs_data['basis_set_elements'][element_Z]

                ecp_shell = {'potential_angular_momentum': shell_am, 'potential_ecp_type': 'scalar'}

                rexponents = []
                gexponents = []
                coefficients = []

                i += 1
                while True:
                    if i >= len(basis_lines) or basis_lines[i][0].isalpha():
                        break

                    line = basis_lines[i].replace('D', 'E')
                    line = line.replace('d', 'E')
                    lsplt = line.split()
                    rexponents.append(int(lsplt[0]))
                    gexponents.append(lsplt[1])
                    coefficients.append(lsplt[2:])
                    i += 1

                ecp_shell['potential_r_exponents'] = rexponents
                ecp_shell['potential_gaussian_exponents'] = gexponents

                # We need to transpose the coefficient matrix
                # (we store a matrix with primitives being the column index and
                # general contraction being the row index)
                ecp_shell['potential_coefficients'] = list(map(list, zip(*coefficients)))

                element_data['element_ecp'].append(ecp_shell)
        i += 1

        # Fix ecp angular momentum now that everything has been read
        for el, v in bs_data['basis_set_elements'].items():
            if not 'element_ecp' in v:
                continue

            max_ecp_am = -1
            for s in v['element_ecp']:
                if s['potential_angular_momentum'] == -1:
                    continue
                max_ecp_am = max(max_ecp_am, max(s['potential_angular_momentum']))

            for s in v['element_ecp']:
                if s['potential_angular_momentum'] == -1:
                    s['potential_angular_momentum'] = [max_ecp_am + 1]

    return bs_data

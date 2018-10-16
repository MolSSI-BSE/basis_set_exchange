from ... import lut


def read_gbasis(basis_lines, fname):
    '''Reads gbasis-formatted file data and converts it to a dictionary with the
       usual BSE fields

       Note that the gbasis format does not store all the fields we
       have, so some fields are left blank
    '''

    skipchars = '!#'
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
    bs_name = None
    while i < len(basis_lines):
        line = basis_lines[i]
        lsplt = line.split(':')
        elementsym = lsplt[0]

        if bs_name is None:
            bs_name = lsplt[1]
        elif lsplt[1] != bs_name:
            raise RuntimeError("Multiple basis sets in a file")

        element_Z = lut.element_Z_from_sym(elementsym)
        element_Z = str(element_Z)

        if not element_Z in bs_data['basis_set_elements']:
            bs_data['basis_set_elements'][element_Z] = {}

        element_data = bs_data['basis_set_elements'][element_Z]

        if not 'element_electron_shells' in element_data:
            element_data['element_electron_shells'] = []

        i += 1

        max_am = int(basis_lines[i].strip())
        i += 1

        for am in range(0, max_am + 1):
            lsplt = basis_lines[i].split()
            shell_am = lut.amchar_to_int(lsplt[0])
            nprim = int(lsplt[1])
            ngen = int(lsplt[2])

            if shell_am[0] != am:
                raise RuntimeError("AM out of order in gbasis?")

            shell = {
                'shell_function_type': 'gto',
                'shell_harmonic_type': 'spherical',
                'shell_region': 'valence',
                'shell_angular_momentum': shell_am
            }

            exponents = []
            coefficients = []

            i += 1
            for j in range(nprim):
                line = basis_lines[i].replace('D', 'E')
                line = line.replace('d', 'E')
                lsplt = line.split()

                if len(lsplt) != (ngen + 1):
                    raise RuntimeError("Incorrect number of general contractions in gbasis")

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

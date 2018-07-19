import os
from .. import lut


def read_g94(basis_path):
    '''Reads a G94-formatted file and converts it to a dictionary with the
       usual BSE fields

       Note that the gaussian format does not store all the fields we
       have, so some fields are left blank
    '''

    skipchars = '!'

    if not os.path.isfile(basis_path):
        raise RuntimeError('G94 basis set path \'{}\' does not exist'.format(basis_path))

    fname = os.path.basename(basis_path)

    with open(basis_path, 'r') as f:
        basis_lines = [l.strip() for l in f]
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
    if basis_lines[0] == '****':
        i += 1  # skip initial ****

    while i < len(basis_lines):
        line = basis_lines[i]
        elementsym = line.split()[0]

        # Some gaussian files have a dash before the element
        if elementsym[0] == '-':
            elementsym = elementsym[1:]

        element_Z = lut.element_Z_from_sym(elementsym)
        element_Z = str(element_Z)

        element_data = {'element_electron_shells': []}

        i += 1
        if "ECP" in basis_lines[i]:
            raise RuntimeError("TODO")
            #maxam = int(lsplt[1])
            #n_elec = int(lsplt[2])

            #i += 1
            #for j in range(maxam + 1):
            #    shell_am = lut.amchar_to_int(basis_lines[i][0])[0]
            #    i += 1
            #    n_entries = int(basis_lines[i])
            #    i += 1

            #    ecp_shell = {'angularMomentum': shell_am}
            #    ecp_exponents = []
            #    ecp_coefficients = []

            #    for k in range(n_entries):
            #        lsplt = basis_lines[i].split()
            #        exp_exponents.append(lsplt[0])
            #        exp_coefficients.append(lsplt[1])
            #        i += 1

            #    bs_data['elements'][element_Z]['ecp'].append(ecp_shell)
        else:
            while basis_lines[i] != '****':
                lsplt = basis_lines[i].split()
                shell_am = lut.amchar_to_int(lsplt[0])
                nshell = int(lsplt[1])

                shell = {
                    'shell_function_type': 'gto',
                    'shell_harmonic_type': 'spherical',
                    'shell_region': 'valence',
                    'shell_angular_momentum': shell_am
                }

                exponents = []
                coefficients = []

                i += 1
                for j in range(nshell):
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
                bs_data['basis_set_elements'][element_Z] = element_data

        i += 1

    return bs_data

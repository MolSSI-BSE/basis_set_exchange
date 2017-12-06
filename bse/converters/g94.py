import os
from .. import lut

skipchars = '!'

def g94_to_json(basis_name, basis_path):
    if not os.path.isfile(basis_path):
        raise RuntimeError('G94 basis set path \'{}\' does not exist'.format(basis_path))

    with open(basis_path, 'r') as f:
        basis_lines = [l.strip() for l in f]
        basis_lines = [l for l in basis_lines if l and not l[0] in skipchars]

    js_data = {'name': basis_name,
               'harmonic': 'cartesian',
               'elements': {}
               }


    i = 1  # skip initial ****
    while i < len(basis_lines):
        line = basis_lines[i]
        elementsym = line.split()[0]
        element_Z = lut.element_data_from_sym(elementsym)[0]

        element_data = {'electronShells':
                          { 'valence':
                              { 'version': "1.0",
                                'shells': []
                               }
                           }
                        }

        i += 1
        if "ECP" in basis_lines[i]:
            maxam = int(lsplt[1])
            n_elec = int(lsplt[2])

            i += 1
            for j in range(maxam+1):
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

from ... import lut
from ..skel import create_skel


def read_g94(basis_lines, fname):
    '''Reads G94-formatted file data and converts it to a dictionary with the
       usual BSE fields

       Note that the gaussian format does not store all the fields we
       have, so some fields are left blank
    '''

    skipchars = '!'
    basis_lines = [l for l in basis_lines if l and not l[0] in skipchars]

    bs_data = create_skel('component')

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

        if not element_Z in bs_data['elements']:
            bs_data['elements'][element_Z] = {}

        element_data = bs_data['elements'][element_Z]

        i += 1

        # Try to guess if this is an ecp
        # Electron basis almost always end in 1.0 (scale factor)
        # ECP lines would end in an integer, so isdecimal() = true for ecp
        if basis_lines[i].split()[-1].isdecimal():
            if not 'ecp_potentials' in element_data:
                element_data['ecp_potentials'] = []

            lsplt = basis_lines[i].split()
            maxam = int(lsplt[1])
            n_elec = int(lsplt[2])
            element_data['ecp_electrons'] = n_elec

            # Highest AM first, then the rest in order
            am_list = list(range(maxam + 1))
            am_list.insert(0, am_list.pop())

            i += 1

            for j in range(maxam + 1):
                i += 1  # Skip the 'title' block - unused according to gaussian docs
                n_entries = int(basis_lines[i])
                i += 1  # Skip title block

                shell_am = am_list[j]
                ecp_shell = {'angular_momentum': [shell_am], 'ecp_type': 'scalar'}
                rexponents = []
                gexponents = []
                coefficients = []

                for k in range(n_entries):
                    lsplt = basis_lines[i].split()
                    rexponents.append(int(lsplt[0]))
                    gexponents.append(lsplt[1])
                    coefficients.append(lsplt[2:])
                    i += 1

                ecp_shell['r_exponents'] = rexponents
                ecp_shell['gaussian_exponents'] = gexponents

                # We need to transpose the coefficient matrix
                # (we store a matrix with primitives being the column index and
                # general contraction being the row index)
                ecp_shell['coefficients'] = list(map(list, zip(*coefficients)))

                element_data['ecp_potentials'].append(ecp_shell)
        else:
            if not 'electron_shells' in element_data:
                element_data['electron_shells'] = []

            while basis_lines[i] != '****':
                lsplt = basis_lines[i].split()
                shell_am = lut.amchar_to_int(lsplt[0])
                nprim = int(lsplt[1])

                shell = {
                    'function_type': 'gto',
                    'harmonic_type': 'spherical',
                    'region': 'valence',
                    'angular_momentum': shell_am
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

                shell['exponents'] = exponents

                # We need to transpose the coefficient matrix
                # (we store a matrix with primitives being the column index and
                # general contraction being the row index)
                shell['coefficients'] = list(map(list, zip(*coefficients)))

                element_data['electron_shells'].append(shell)

            i += 1

    return bs_data

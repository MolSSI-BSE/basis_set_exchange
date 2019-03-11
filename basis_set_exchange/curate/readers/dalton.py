from ..skel import create_skel


def read_dalton(basis_lines, fname):
    '''Reads Dalton-formatted file data and converts it to a dictionary with the
       usual BSE fields

       Note that the nwchem format does not store all the fields we
       have, so some fields are left blank
    '''

    skipchars = '$'
    basis_lines = [l for l in basis_lines if l and not l[0] in skipchars]

    bs_data = create_skel('component')

    i = 0

    while i < len(basis_lines):
        line = basis_lines[i]

        if line.lower().startswith('a '):
            element_Z = line.split()[1]
            i += 1

            # Shell am is strictly increasing (I hope)
            shell_am = 0

            while i < len(basis_lines) and not basis_lines[i].lower().startswith('a '):
                line = basis_lines[i]
                nprim, ngen = line.split()

                if not element_Z in bs_data['elements']:
                    bs_data['elements'][element_Z] = {}
                if not 'electron_shells' in bs_data['elements'][element_Z]:
                    bs_data['elements'][element_Z]['electron_shells'] = []

                element_data = bs_data['elements'][element_Z]

                shell = {
                    'function_type': 'gto',
                    'harmonic_type': 'spherical',
                    'region': '',
                    'angular_momentum': [shell_am]
                }

                exponents = []
                coefficients = []

                i += 1
                for _ in range(int(nprim)):
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

                # Make sure the number of general contractions is >0
                # (This error was found in some bad files)
                if int(ngen) <= 0:
                    raise RuntimeError("Number of general contractions is not greater than zero for element " + str(element_Z))

                # Make sure the number of general contractions match the heading line
                if len(shell['coefficients']) != int(ngen):
                    raise RuntimeError("Number of general contractions does not equal what was given for element " + str(element_Z))

                element_data['electron_shells'].append(shell)
                shell_am += 1

    return bs_data

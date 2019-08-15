from ... import lut
from ..skel import create_skel


def read_cfour(basis_lines, fname):
    '''Reads gbasis-formatted file data and converts it to a dictionary with the
       usual BSE fields

       Note that the gbasis format does not store all the fields we
       have, so some fields are left blank
    '''

    skipchars = '!#'
    basis_lines = [l for l in basis_lines if l and not l[0] in skipchars]

    bs_data = create_skel('component')

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

        if not element_Z in bs_data['elements']:
            bs_data['elements'][element_Z] = {}

        element_data = bs_data['elements'][element_Z]

        if not 'electron_shells' in element_data:
            element_data['electron_shells'] = []

        i += 2  # Skip comment line

        nshell = int(basis_lines[i].strip())
        i += 1

        # Read in the AM, ngeneral, and nprim for each shell
        # This is in a block just after nshell
        all_am = [int(x.strip()) for x in basis_lines[i].split()]
        i += 1
        all_ngen = [int(x.strip()) for x in basis_lines[i].split()]
        i += 1
        all_nprim = [int(x.strip()) for x in basis_lines[i].split()]
        i += 1

        assert len(all_am) == nshell
        assert len(all_ngen) == nshell
        assert len(all_nprim) == nshell

        for shell_idx in range(nshell):
            shell_am = [all_am[shell_idx]]
            ngen = all_ngen[shell_idx]
            nprim = all_nprim[shell_idx]

            if max(shell_am) <= 1:
                func_type = 'gto'
            else:
                func_type = 'gto_spherical'

            shell = {'function_type': func_type, 'region': '', 'angular_momentum': shell_am}

            exponents = []
            coefficients = []

            # Read in exponents block
            while len(exponents) < nprim:
                line = basis_lines[i].replace('D', 'E')
                line = line.replace('d', 'E')
                exponents.extend([x.strip() for x in line.split()])
                i += 1

            # Read in all coefficients
            for prim in range(nprim):
                coef_tmp = []
                while len(coef_tmp) < ngen:
                    line = basis_lines[i].replace('D', 'E')
                    line = line.replace('d', 'E')
                    coef_tmp.extend([x.strip() for x in line.split()])
                    i += 1
                coefficients.append(coef_tmp)

            shell['exponents'] = exponents

            # We need to transpose the coefficient matrix
            # (we store a matrix with primitives being the column index and
            # general contraction being the row index)
            shell['coefficients'] = list(map(list, zip(*coefficients)))

            element_data['electron_shells'].append(shell)

    return bs_data

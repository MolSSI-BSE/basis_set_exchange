from ... import lut
from ..skel import create_skel
from ...api import get_basis

# Dict for solving the difference in the naming convention for Ahlrichs basis set in Gaussian
# Specifically for Def2SV, Def2SVP, Def2SVPP, Def2TZV, Def2TZVP, Def2TZVPP, Def2QZV, Def2QZVP, Def2QZVPP

name_dict = {'DEF2SV': 'def2-SV', 'DEF2SVP': 'def2-SVP', 'DEF2SVPP': 'def2-SVPP', 'DEF2TZV': 'def2-TZV',
             'DEF2TZVP': 'def2-TZVP', 'DEF2TZVPP': 'def2-TZVPP', 'DEF2QZV': 'def2-QZV', 'DEF2QZVP': 'def2-QZVP',
             'DEF2QZVPP': 'def2-QZVPP'}

def append_data(current_bs, new_bs, element):
    if not element in current_bs['elements']:
        current_bs['elements'][element] = {}
        current_bs['elements'][element]['electron_shells'] = []

    if new_bs['elements'][element]['electron_shells']:
        current_bs['elements'][element]['electron_shells'].extend(
            new_bs['elements'][element]['electron_shells'])

    if new_bs['elements'][element]['references']:
        try:
            current_bs['elements'][element]['references'].extend(
                new_bs['elements'][element]['references'])
        except KeyError:
            current_bs['elements'][element]['references'] = new_bs['elements'][element]['references']

    if 'function_types' in current_bs:
        for function in new_bs['function_types']:
            if not function in current_bs['function_types']:
                current_bs['function_types'].append(function)
    else:
        current_bs['function_types'] = new_bs['function_types']

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

        # check for additional **** in the end
        if line == '****':
            i += 1
            continue

        split_line = line.split()

        # Check for a specific type of format
        # Example:
        # ****
        # -Li -Be -B  -C  -N  -O  -F  -Ne 0
        # def2SVP
        # ****

        if len(split_line) > 2 and split_line[-1] == '0':
            # read elements
            elementsyms = []
            for elementsym in split_line[:-1]:
                if elementsym[0] == '-':
                    elementsyms.append(elementsym[1:])
                else:
                    elementsyms.append(elementsym)

            i += 1
            # read basis set
            name = basis_lines[i]

            for elementsym in elementsyms:
                try:
                    # fmt=None for specifying getint the dict
                    new_basis_set = get_basis(name, elements=elementsym, fmt=None)
                except KeyError:
                    # print('{} basis set for element {} not found.'.format(name, elementsym))
                    new_basis_set = get_basis(name_dict[name.upper()], elements=elementsym, fmt=None)
                    # print('Assume the {} basis set is enquired.'.format(name_dict[name.upper()]))

                element_Z = lut.element_Z_from_sym(elementsym)
                element_Z = str(element_Z)
                append_data(bs_data, new_basis_set, element_Z)

            i += 1
            continue

        elementsym = split_line[0]

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
                ecp_shell = {'angular_momentum': [shell_am], 'ecp_type': 'scalar_ecp'}
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

                # check if reference to other basis set
                # Example form:
                # -H     0
                # def2TZVP
                # ****
                if len(lsplt) == 1:
                    # add the data from existing basis set
                    name = lsplt[0]
                    try:
                        # fmt=None for specifying getint the dict
                        new_basis_set = get_basis(name, elements=elementsym, fmt=None)
                    except KeyError:
                        # print('{} basis set for element {} not found.'.format(name, elementsym))
                        new_basis_set = get_basis(name_dict[name.upper()], elements=elementsym, fmt=None)
                        # print('Assume the {} basis set is enquired.'.format(name_dict[name.upper()]))

                    append_data(bs_data, new_basis_set, element_Z)
                    i += 1
                else:
                    shell_am = lut.amchar_to_int(lsplt[0], hij=True)
                    nprim = int(lsplt[1])

                    if max(shell_am) <= 1:
                        func_type = 'gto'
                    else:
                        func_type = 'gto_spherical'

                    shell = {'function_type': func_type, 'region': '', 'angular_momentum': shell_am}

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

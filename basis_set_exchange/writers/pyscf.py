'''
Conversion of basis sets to PySCF format

17 Nov 2021 Susi Lehtola
'''

from .. import lut, manip, sort


def write_pyscf(basis):
    '''Converts a basis set to PySCF format'''

    r = {}

    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis['elements'][z]

            sym = lut.element_sym_from_Z(z, True)

            # List of shells
            atom_shells = []
            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                ncontr = len(coefficients)
                nprim = len(exponents)
                am = shell['angular_momentum']
                assert len(am) == 1

                shell_data = [am[0]]
                for iprim in range(nprim):
                    row = [float(coefficients[ic][iprim]) for ic in range(ncontr)]
                    row.insert(0, float(exponents[iprim]))
                    shell_data.append(row)
                atom_shells.append(shell_data)
            r[sym] = atom_shells

    return r


def write_pyscf_ecp(basis):
    '''Converts an ECP basis set to PySCF format'''

    r = {}

    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if ecp_elements:
        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, True)
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

            # Sort lowest->highest
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])

            # List of ECP
            atom_ecp = [data['ecp_electrons'], []]
            for ir, pot in enumerate(ecp_list):
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']
                am = pot['angular_momentum']
                nprim = len(rexponents)

                shell_data = [am[0], []]
                # PySCF wants the data in order of rexp=0, 1, 2, ..
                for rexpval in range(max(rexponents) + 1):
                    rcontr = []
                    for i in range(nprim):
                        if rexponents[i] == rexpval:
                            rcontr.append([float(gexponents[i]), float(coefficients[0][i])])
                    shell_data[1].append(rcontr)
                atom_ecp[1].append(shell_data)
            r[sym] = atom_ecp

    return r

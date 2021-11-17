'''
Conversion of basis sets to PySCF format

17 Nov 2021 Susi Lehtola
'''

from .. import lut, manip, sort, printing

def write_pyscf(basis):
    '''Converts a basis set to PySCF format'''

    r = {}

    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

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

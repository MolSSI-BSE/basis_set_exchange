"""
Conversion of basis sets to deMon2K format
"""

from .. import lut, manip, sort, misc, printing


def write_demon2k(basis):
    """Converts a basis set to deMon2K format"""

    if "gto_spherical" in basis["function_types"]:
        s = "# This basis set uses spherical components\n\n"
    else:
        s = "# This basis set uses cartesian components\n\n"

    basis = manip.uncontract_spdf(basis, 0, True)
    basis = manip.uncontract_general(basis, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis["elements"].items() if "electron_shells" in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis["elements"].items() if "ecp_potentials" in v]

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis["elements"][z]
            sym = lut.element_sym_from_Z(z, True)
            elname = lut.element_name_from_Z(z).upper()
            cont_string = misc.contraction_string(data)

            # Need the start of electron shells if there are ECPs
            ecp_electrons = data.get("ecp_electrons", 0)
            shells_start = lut.electron_shells_start(ecp_electrons)
            shells_start = list(shells_start)

            s += "O-{} {} ({})\n".format(elname, sym.upper(), basis["name"])
            s += "# {}\n".format(cont_string)

            nshells = len(data["electron_shells"])
            s += "    {}\n".format(nshells)

            for shell in data["electron_shells"]:
                exponents = shell["exponents"]
                coefficients = shell["coefficients"]
                ncol = len(coefficients) + 1
                nprim = len(exponents)

                # We removed spdf already
                assert len(shell["angular_momentum"]) == 1
                am = shell["angular_momentum"][0]

                # shells_start has starting principal quantum numbers for all AM
                pqn = shells_start[am]
                shells_start[am] += 1
                s += "    {}    {}    {}\n".format(pqn, am, nprim)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=False)

    # Write out ECP
    if ecp_elements:
        s += "\n\nECP\n"
        for z in ecp_elements:
            data = basis["elements"][z]
            sym = lut.element_sym_from_Z(z, normalize=True)
            max_ecp_am = max([x["angular_momentum"][0] for x in data["ecp_potentials"]])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data["ecp_potentials"], key=lambda x: x["angular_momentum"])
            ecp_list.insert(0, ecp_list.pop())

            s += "{} nelec {}\n".format(sym, data["ecp_electrons"])

            for pot in ecp_list:
                rexponents = pot["r_exponents"]
                gexponents = pot["gaussian_exponents"]
                coefficients = pot["coefficients"]

                am = pot["angular_momentum"]
                amchar = lut.amint_to_char(am).upper()

                if am[0] == max_ecp_am:
                    s += "{} ul\n".format(sym)
                else:
                    s += "{} {}\n".format(sym, amchar)

                point_places = [0, 9, 32]
                s += printing.write_matrix([rexponents, gexponents, *coefficients], point_places, convert_exp=False)

        s += "END\n"

    return s

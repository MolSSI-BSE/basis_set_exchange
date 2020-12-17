"""
Conversion of basis sets to Dalton format
"""

from .. import lut, manip, sort, misc, printing


def write_dalton(basis):
    """Converts a basis set to Dalton format"""

    s = "! Basis = {}\n\n".format(basis["name"])

    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [
        k for k, v in basis["elements"].items() if "electron_shells" in v
    ]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis["elements"].items() if "ecp_potentials" in v]

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis["elements"][z]
            # sym = lut.element_sym_from_Z(z, True)
            elname = lut.element_name_from_Z(z).upper()
            cont_string = misc.contraction_string(data)

            s += "a {}\n".format(z)
            s += "! {}       {}\n".format(elname, cont_string)

            for shell in data["electron_shells"]:
                exponents = shell["exponents"]
                coefficients = shell["coefficients"]
                ncol = len(coefficients) + 1
                nprim = len(exponents)
                ngen = len(coefficients)

                am = shell["angular_momentum"]
                amchar = lut.amint_to_char(am, hij=True)
                s += "! {} functions\n".format(amchar)

                # Is this a bug in the original EMSL?
                # s += '{}   {}   1.00\n'.format(sym, r, nprim)
                s += "{}    {}    {}\n".format("H", nprim, ngen)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix(
                    [exponents, *coefficients], point_places, convert_exp=False
                )

    # Write out ECP
    if ecp_elements:
        s += "\n\nECP\n"
        for z in ecp_elements:
            data = basis["elements"][z]
            sym = lut.element_sym_from_Z(z, normalize=True)
            max_ecp_am = max([x["angular_momentum"][0] for x in data["ecp_potentials"]])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(
                data["ecp_potentials"], key=lambda x: x["angular_momentum"]
            )
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
                s += printing.write_matrix(
                    [rexponents, gexponents, *coefficients],
                    point_places,
                    convert_exp=False,
                )

        s += "END\n"
    return s

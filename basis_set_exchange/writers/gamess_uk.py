"""
Conversion of basis sets to GAMESS-UK format
"""

from .. import lut, manip, sort, printing


def write_gamess_uk(basis):
    """Converts a basis set to GAMESS-UK"""

    s = ""

    # Uncontract all but SP
    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 1, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [
        k for k, v in basis["elements"].items() if "electron_shells" in v
    ]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis["elements"].items() if "ecp_potentials" in v]

    # Electron Basis
    if electron_elements:
        # electronic part starts with $DATA

        for z in electron_elements:
            data = basis["elements"][z]

            el_name = lut.element_name_from_Z(z).upper()
            el_sym = lut.element_sym_from_Z(z, normalize=True)
            s += "\n"
            s += "# " + el_name + "\n"

            for shell in data["electron_shells"]:
                exponents = shell["exponents"]
                coefficients = shell["coefficients"]
                ncol = len(coefficients) + 2  # include index column

                am = shell["angular_momentum"]
                amchar = lut.amint_to_char(am, hij=True, use_L=True).upper()
                s += "{}   {}\n".format(amchar, el_sym)

                # 1-based indexing
                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol)]

                # Note: order for sp shells is (coeff of s) (exponents) (coeff of p)
                s += printing.write_matrix(
                    [coefficients[0], exponents, *coefficients[1:]], point_places
                )

    # Write out ECP
    if ecp_elements:
        s += "\n\nEffective Core Potentials\n"
        s += "---------------------------\n"

        for z in ecp_elements:
            data = basis["elements"][z]
            sym = lut.element_sym_from_Z(z).upper()
            max_ecp_am = max([x["angular_momentum"][0] for x in data["ecp_potentials"]])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(
                data["ecp_potentials"], key=lambda x: x["angular_momentum"]
            )
            ecp_list.insert(0, ecp_list.pop())

            s += "CARDS {}\n".format(sym)
            s += "    {}     {}\n".format(max_ecp_am, data["ecp_electrons"])

            for pot in ecp_list:
                rexponents = pot["r_exponents"]
                gexponents = pot["gaussian_exponents"]
                coefficients = pot["coefficients"]

                point_places = [1, 9, 32]
                s += printing.write_matrix(
                    [rexponents, *coefficients, gexponents], point_places
                )
            s += "\n"
    return s

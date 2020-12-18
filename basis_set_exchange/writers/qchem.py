"""
Conversion of basis sets to Q-Chem format
"""

from .. import lut, manip, sort, printing


def _determine_pure(basis):
    # starts at d shells
    pure = {}
    for eldata in basis["elements"].values():
        if "electron_shells" not in eldata:
            continue
        for sh in eldata["electron_shells"]:
            for shell_am in sh["angular_momentum"]:
                harm = "2"  # cartesian
                if "spherical" in sh["function_type"]:
                    harm = "1"

                if shell_am in pure:
                    pure[shell_am] = harm if harm == "1" else pure[shell_am]
                else:
                    pure[shell_am] = harm

    pure_list = sorted(pure.items(), reverse=True)
    pure_list = pure_list[:-2]  # Trim s & p
    return "".join(x[1] for x in pure_list)


def write_qchem(basis):
    """Converts a basis set to Q-Chem

    Q-Chem is basically gaussian format, wrapped in $basis/$end

    This also outputs the PURECART variable of the $rem block
    """

    s = ""
    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 1, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis["elements"].items() if "electron_shells" in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis["elements"].items() if "ecp_potentials" in v]

    purecart = _determine_pure(basis)
    if purecart != "":
        s += "$rem\n"
        if electron_elements:
            s += "    BASIS GEN\n"
        if ecp_elements:
            s += "    ECP GEN\n"
        s += "    PURECART " + _determine_pure(basis) + "\n"
        s += "$end\n\n"

    # Electron Basis
    if electron_elements:
        s += "$basis\n"
        for z in electron_elements:
            data = basis["elements"][z]

            sym = lut.element_sym_from_Z(z, True)
            s += "{}     0\n".format(sym)

            for shell in data["electron_shells"]:
                exponents = shell["exponents"]
                coefficients = shell["coefficients"]
                ncol = len(coefficients) + 1
                nprim = len(exponents)

                am = shell["angular_momentum"]
                amchar = lut.amint_to_char(am, hij=True).upper()

                s += "{}   {}   1.00\n".format(amchar, nprim)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=True)

            s += "****\n"
        s += "$end\n"

    # Write out ECP
    if ecp_elements:
        s += "\n\n$ecp\n"
        for z in ecp_elements:
            data = basis["elements"][z]
            sym = lut.element_sym_from_Z(z).upper()
            max_ecp_am = max([x["angular_momentum"][0] for x in data["ecp_potentials"]])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data["ecp_potentials"], key=lambda x: x["angular_momentum"])
            ecp_list.insert(0, ecp_list.pop())

            s += "{}     0\n".format(sym)
            s += "{}-ECP     {}     {}\n".format(sym, max_ecp_am, data["ecp_electrons"])

            for pot in ecp_list:
                rexponents = pot["r_exponents"]
                gexponents = pot["gaussian_exponents"]
                coefficients = pot["coefficients"]
                nprim = len(rexponents)

                am = pot["angular_momentum"]
                amchar = lut.amint_to_char(am, hij=True)

                if am[0] == max_ecp_am:
                    s += "{} potential\n".format(amchar)
                else:
                    s += "{}-{} potential\n".format(amchar, max_ecp_amchar)

                s += "  " + str(nprim) + "\n"

                point_places = [0, 9, 32]
                s += printing.write_matrix([rexponents, gexponents, *coefficients], point_places, convert_exp=True)
            s += "****\n"
        s += "$end\n"

    return s

'''
Comparison of basis data against authoritative sources
'''

from ..api import get_basis
from ..misc import compact_elements
from ..sort import sort_shells, sort_potentials
from .. import manip
from .readers import read_formatted_basis
from .compare import _reldiff


def _print_list(lst):
    '''
    Prints a list from a comparison
    '''

    a = compact_elements(lst)
    if a is not None:
        return a
    else:
        return ""


def shells_difference(s1, s2):
    """
    Computes and prints the differences between two lists of shells

    If the shells contain a different number primitives,
    or the lists are of different length, inf is returned.
    Otherwise, the maximum relative difference is returned.
    """

    max_rdiff = 0.0
    nsh = len(s1)
    if len(s2) != nsh:
        print("Different number of shells: {} vs {}".format(len(s1), len(s2)))
        return float('inf')

    shells1 = sort_shells(s1)
    shells2 = sort_shells(s2)

    for n in range(nsh):
        sh1 = shells1[n]
        sh2 = shells2[n]

        if sh1['angular_momentum'] != sh2['angular_momentum']:
            print("Different angular momentum for shell {}".format(n))
            return float('inf')

        nprim = len(sh1['exponents'])
        if len(sh2['exponents']) != nprim:
            print("Different number of primitives for shell {}".format(n))
            return float('inf')

        ngen = len(sh1['coefficients'])
        if len(sh2['coefficients']) != ngen:
            print("Different number of general contractions for shell {}".format(n))
            return float('inf')

        for p in range(nprim):
            e1 = sh1['exponents'][p]
            e2 = sh2['exponents'][p]
            r = _reldiff(e1, e2)
            if r > 0.0:
                print("   Exponent {:3}: {:20} {:20} -> {:16.8e}".format(p, e1, e2, r))
            max_rdiff = max(max_rdiff, r)

            for g in range(ngen):
                c1 = sh1['coefficients'][g][p]
                c2 = sh2['coefficients'][g][p]
                r = _reldiff(c1, c2)
                if r > 0.0:
                    print("Coefficient {:3}: {:20} {:20} -> {:16.8e}".format(p, c1, c2, r))
                max_rdiff = max(max_rdiff, r)

    print()
    print("Max relative difference for these shells: {}".format(max_rdiff))
    return max_rdiff


def potentials_difference(p1, p2):
    """
    Computes and prints the differences between two lists of potentials

    If the shells contain a different number primitives,
    or the lists are of different length, inf is returned.
    Otherwise, the maximum relative difference is returned.
    """

    max_rdiff = 0.0
    np = len(p1)
    if len(p2) != np:
        print("Different number of potentials")
        return float('inf')

    pots1 = sort_potentials(p1)
    pots2 = sort_potentials(p2)

    for n in range(np):
        pot1 = pots1[n]
        pot2 = pots2[n]

        if pot1['angular_momentum'] != pot2['angular_momentum']:
            print("Different angular momentum for potential {}".format(n))
            return float('inf')

        nprim = len(pot1['gaussian_exponents'])
        if len(pot2['gaussian_exponents']) != nprim:
            print("Different number of primitives for potential {}".format(n))
            return float('inf')

        ngen = len(pot1['coefficients'])
        if len(pot2['coefficients']) != ngen:
            print("Different number of general contractions for potential {}".format(n))
            return float('inf')

        for p in range(nprim):
            e1 = pot1['gaussian_exponents'][p]
            e2 = pot2['gaussian_exponents'][p]
            r = _reldiff(e1, e2)
            if r > 0.0:
                print("   Gaussian Exponent {:3}: {:20} {:20} -> {:16.8e}".format(p, e1, e2, r))
            max_rdiff = max(max_rdiff, r)

            e1 = pot1['r_exponents'][p]
            e2 = pot2['r_exponents'][p]
            r = _reldiff(e1, e2)
            if r > 0.0:
                print("          R Exponent {:3}: {:20} {:20} -> {:16.8e}".format(p, e1, e2, r))
            max_rdiff = max(max_rdiff, r)

            for g in range(ngen):
                c1 = pot1['coefficients'][g][p]
                c2 = pot2['coefficients'][g][p]
                r = _reldiff(c1, c2)
                if r > 0.0:
                    print("         Coefficient {:3}: {:20} {:20} -> {:16.8e}".format(p, c1, c2, r))
                max_rdiff = max(max_rdiff, r)

    print()
    print("Max relative difference for these potentials: {}".format(max_rdiff))
    return max_rdiff


def basis_comparison_report(bs1, bs2, uncontract_general=False):
    '''
    Compares two basis set dictionaries and prints a report about their differences
    '''

    all_bs1 = list(bs1['elements'].keys())

    if uncontract_general:
        bs1 = manip.uncontract_general(bs1)
        bs2 = manip.uncontract_general(bs2)

    not_in_bs1 = []  # Found in bs2, not in bs1
    not_in_bs2 = all_bs1.copy()  # Found in bs1, not in bs2
    no_diff = []  # Elements for which there is no difference
    some_diff = []  # Elements that are different
    big_diff = []  # Elements that are substantially different

    for k, v in bs2['elements'].items():
        if k not in all_bs1:
            not_in_bs1.append(k)
            continue

        print()
        print("-------------------------------------")
        print(" Element ", k)
        bs1_el = bs1['elements'][k]

        max_rdiff_el = 0.0
        max_rdiff_ecp = 0.0

        # Check to make sure that neither or both have ecp/electron shells
        if 'electron_shells' in v and 'electron_shells' not in bs1_el:
            print("bs2 has electron_shells, but bs1 does not")
            max_rdiff_el = float('inf')
        if 'electron_shells' in bs1_el and 'electron_shells' not in v:
            print("bs1 has electron_shells, but bs2 does not")
            max_rdiff_el = float('inf')
        if 'ecp_potentials' in v and 'ecp_potentials' not in bs1_el:
            print("bs2 has ecp_potentials, but bs1 does not")
            max_rdiff_ecp = float('inf')
        if 'ecp_potentials' in bs1_el and 'ecp_potentials' not in v:
            print("bs1 has ecp_potentials, but bs2 does not")
            max_rdiff_ecp = float('inf')

        if 'electron_shells' in v and 'electron_shells' in bs1_el:
            max_rdiff_el = max(max_rdiff_el, shells_difference(v['electron_shells'], bs1_el['electron_shells']))
        if 'ecp_potentials' in v and 'ecp_potentials' in bs1_el:
            nel1 = v['ecp_electrons']
            nel2 = bs1_el['ecp_electrons']
            if int(nel1) != int(nel2):
                print('Different number of electrons replaced by ECP ({} vs {})'.format(nel1, nel2))
                max_rdiff_ecp = float('inf')
            else:
                max_rdiff_ecp = max(max_rdiff_ecp, potentials_difference(v['ecp_potentials'],
                                                                         bs1_el['ecp_potentials']))

        max_rdiff = max(max_rdiff_el, max_rdiff_ecp)

        # Handle some differences
        if max_rdiff == float('inf'):
            big_diff.append(k)
        elif max_rdiff == 0.0:
            no_diff.append(k)
        else:
            some_diff.append(k)

        not_in_bs2.remove(k)

    print()
    print("     Not in bs1: ", _print_list(not_in_bs1))
    print("     Not in bs2: ", _print_list(not_in_bs2))
    print("  No difference: ", _print_list(no_diff))
    print("Some difference: ", _print_list(some_diff))
    print(" BIG difference: ", _print_list(big_diff))
    print()

    return (len(not_in_bs1) == 0 and len(not_in_bs2) == 0 and len(some_diff) == 0 and len(big_diff) == 0)


def compare_basis_against_file(basis_name,
                               src_filepath,
                               file_type=None,
                               version=None,
                               uncontract_general=False,
                               data_dir=None):
    '''Compare a basis set in the BSE against a reference file'''

    src_data = read_formatted_basis(src_filepath, file_type)
    bse_data = get_basis(basis_name, version=version, data_dir=data_dir)
    return basis_comparison_report(src_data, bse_data, uncontract_general=uncontract_general)


def compare_basis_files(file_path_1, file_path_2, file_type_1=None, file_type_2=None, uncontract_general=False):
    '''Compare two files containing formatted basis sets'''

    bs1 = read_formatted_basis(file_path_1, file_type_1)
    bs2 = read_formatted_basis(file_path_2, file_type_2)
    return basis_comparison_report(bs1, bs2, uncontract_general)


def compare_basis_sets(basis_name_1,
                       basis_name_2,
                       version_1=None,
                       version_2=None,
                       uncontract_general=False,
                       data_dir_1=None,
                       data_dir_2=None):
    '''Compare two files containing formatted basis sets'''

    bs1 = get_basis(basis_name_1, version=version_1, data_dir=data_dir_1)
    bs2 = get_basis(basis_name_2, version=version_2, data_dir=data_dir_2)
    return basis_comparison_report(bs1, bs2, uncontract_general)

'''
Comparison of basis data against authoritative sources
'''

from ..api import get_basis
from ..misc import compact_elements
from .readers import read_formatted_basis
from .compare import shells_difference, potentials_difference
from .. import manip


def _print_list(lst):
    '''
    Prints a list from a comparison
    '''

    a = compact_elements(lst)
    if a is not None:
        return a
    else:
        return ""


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

        if 'electron_shells' in v:
            max_rdiff_el = shells_difference(v['electron_shells'], bs1_el['electron_shells'])
        if 'ecp_potentials' in v:
            nel1 = v['element_ecp_electrons']
            nel2 = bs1_el['element_ecp_electrons']
            if int(nel1) != int(nel2):
                print('Different number of electrons replaced by ECP ({} vs {})'.format(nel1, nel2))
                max_rdiff_ecp = float('inf')
            else:
                max_rdiff_ecp = potentials_difference(v['ecp_potentials'], bs1_el['ecp_potentials'])
                v['ecp_potentials'] = bs1_el['ecp_potentials']

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

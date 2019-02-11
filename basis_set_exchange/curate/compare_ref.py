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


def compare_basis_against_ref(basis_name,
                              src_filepath,
                              file_type=None,
                              version=None,
                              uncontract_general=False,
                              data_dir=None):
    '''
    Compares basis set data from an authoritative source against bse data
    '''

    src_data = read_formatted_basis(src_filepath, file_type)
    bse_data = get_basis(basis_name, version=version, data_dir=data_dir)

    all_src = list(src_data['basis_set_elements'].keys())

    if uncontract_general:
        src_data = manip.uncontract_general(src_data)
        bse_data = manip.uncontract_general(bse_data)

    not_in_src = []  # Found in BSE, not in the reference
    not_in_bse = all_src.copy()  # Found in the reference, not in the BSE
    no_diff = []  # Elements for which there is no difference
    some_diff = []  # Elements that are different
    big_diff = []  # Elements that are substantially different

    for k, v in bse_data['basis_set_elements'].items():
        if k not in all_src:
            not_in_src.append(k)
            continue

        print()
        print("-------------------------------------")
        print(" Element ", k)
        src_el = src_data['basis_set_elements'][k]

        max_rdiff_el = 0.0
        max_rdiff_ecp = 0.0

        if 'element_electron_shells' in v:
            max_rdiff_el = shells_difference(v['element_electron_shells'], src_el['element_electron_shells'])
        if 'element_ecp' in v:
            max_rdiff_ecp = potentials_difference(v['element_ecp'], src_el['element_ecp'])
            v['element_ecp'] = src_el['element_ecp']

        max_rdiff = max(max_rdiff_el, max_rdiff_ecp)

        # Handle some differences
        if max_rdiff == float('inf'):
            big_diff.append(k)
        elif max_rdiff == 0.0:
            no_diff.append(k)
        else:
            some_diff.append(k)

        not_in_bse.remove(k)

    print()
    print("     Not in src: ", _print_list(not_in_src))
    print("     Not in bse: ", _print_list(not_in_bse))
    print("  No difference: ", _print_list(no_diff))
    print("Some difference: ", _print_list(some_diff))
    print(" BIG difference: ", _print_list(big_diff))
    print()

    return (len(not_in_src) == 0 and len(not_in_bse) == 0 and len(some_diff) == 0 and len(big_diff) == 0)

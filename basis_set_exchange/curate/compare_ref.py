'''
Comparison of basis data against authoritative sources
'''

from .. import get_basis
from ..misc import compact_elements
from .compare import shells_difference,potentials_difference
from .read_turbomole import read_turbomole

def _fix_uncontracted(basis):
    '''
    Forces the contraction coefficient of uncontracted shells to 1.0
    '''

    for el in basis['basis_set_elements'].values():
        if 'element_electron_shells' not in el:
            continue

        for sh in el['element_electron_shells']:
            if len(sh['shell_coefficients']) == 1 and len(sh['shell_coefficients'][0]) == 1:
                    sh['shell_coefficients'][0][0] = '1.0000000'

            # Some uncontracted shells don't have a coefficient
            if len(sh['shell_coefficients']) == 0:
                sh['shell_coefficients'].append(['1.0000000'])

    return basis


def _print_list(lst):
    '''
    Prints a list from a comparison
    '''

    a = compact_elements(lst)
    if a is not None:
        return a
    else:
        return ""


def _compare_basis_against_ref(basis_name, src_data, version=None):
    '''
    Compares basis set data from an authoritative source against bse data
    '''
    bse_data = get_basis(basis_name, version=version)
    all_src = list(src_data['basis_set_elements'].keys())

    not_in_src = [] # Found in BSE, not in the reference
    not_in_bse = all_src.copy()  # Found in the reference, not in the BSE
    no_diff = []    # Elements for which there is no difference
    some_diff = [] # Elements that are different
    big_diff = []  # Elements that are substantially different

    for k,v in bse_data['basis_set_elements'].items():
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
            print()
            v['element_electron_shells'] = src_el['element_electron_shells']
        if 'element_ecp' in v:
            max_rdiff_ecp = potentials_difference(v['element_ecp'], src_el['element_ecp'])
            v['element_ecp'] = src_el['element_ecp']
            print()

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


def compare_basis_against_ref(basis_name, src_filepath, file_type, version=None):
    '''
    Compares basis set data from an authoritative source against bse data
    '''

    type_readers = { 'turbomole': read_turbomole }

    if file_type not in type_readers:
        raise RuntimeError("Unknown file type to read '{}'".format(file_type))

    src_data = type_readers[file_type](src_filepath)
    src_data = _fix_uncontracted(src_data)
    _compare_basis_against_ref(basis_name, src_data, version)

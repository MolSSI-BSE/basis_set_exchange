'''
Comparison of basis data against authoritative sources
'''

import copy
from ..fileio import read_json_basis, write_json_basis
from ..api import get_basis
from ..misc import compact_elements
from .readers import read_formatted_basis
from .compare import shells_difference, potentials_difference, compare_electron_shells
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


def _replace_shell_data(old_shells, src_shells):
    '''
    Replaces exponents and coefficients of old_data with that in src_data
    '''

    new_shells = []
    for sh1 in src_shells:
        # Find its likely candidate in old_shells
        for sh2 in old_shells:
            if compare_electron_shells(sh1, sh2, rel_tol=0.0):
                new_shells.append(sh2)
                break
            elif compare_electron_shells(sh1, sh2, rel_tol=1e-3):
                sh_tmp = copy.deepcopy(sh2)
                sh_tmp['shell_exponents'] = sh1['shell_exponents']
                sh_tmp['shell_coefficients'] = sh1['shell_coefficients']
                new_shells.append(sh_tmp)
                break
        else:
            sh_tmp = copy.deepcopy(sh1)
            sh_tmp['data_source'] = None
            new_shells.append(sh_tmp)

    return new_shells


def _replace_ecp_data(old_pots, src_pots):
    '''
    Replaces ECP exponents and coefficients of old_data with that in src_data
    '''

    new_pots = []
    for pot1 in src_pots:
        # Find its likely candidate in old_pots
        for pot2 in old_pots:
            if compare_ecp_pots(pot1, pot2, rel_tol=0.0):
                new_pots.append(pot2)
                break
            elif compare_ecp_pots(pot1, pot2, rel_tol=1e-3):
                pot_tmp = copy.deepcopy(pot2)
                pot_tmp['potential_r_exponents'] = pot1['potential_r_exponents']
                pot_tmp['potential_gaussian_exponents'] = pot1['potential_gaussian_exponents']
                pot_tmp['potential_coefficients'] = pot1['potential_coefficients']
                new_pots.append(pot_tmp)
                break
        else:
            pot_tmp = copy.deepcopy(pot1)
            pot_tmp['data_source'] = None
            new_pots.append(pot_tmp)

    return new_pots


def compare_basis_against_ref(basis_name, src_filepath, file_type=None, version=None, uncontract_general=False):
    '''
    Compares basis set data from an authoritative source against bse data
    '''

    src_data = read_formatted_basis(src_filepath, file_type)
    bse_data = get_basis(basis_name, version=version)

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


def replace_basis_data(basis_name, src_filepath, file_type=None, version=None, inplace=False,
                       uncontract_general=False):
    '''
    Replaces data in basis set files with those from a reference

    Data is replaced only if it doesn't exactly match.

    If inplace is True, then the data in the original files is overwritten.
    Otherwise, the new data is written to a file with the same name, but
    ending with .diff
    '''

    src_data = read_formatted_basis(src_filepath, file_type)
    bse_data = get_basis(basis_name, version=version)

    if uncontract_general:
        src_data = manip.uncontract_general(src_data)
        bse_data = manip.uncontract_general(bse_data)

    all_src = list(src_data['basis_set_elements'].keys())

    not_in_src = []  # Found in BSE, not in the reference
    not_in_bse = all_src.copy()  # Found in the reference, not in the BSE

    replace_map = {}
    for k, v in bse_data['basis_set_elements'].items():
        if k not in all_src:
            not_in_src.append(k)
            continue
        not_in_bse.remove(k)

        src_el = src_data['basis_set_elements'][k]

        new_shells = []
        new_pots = []
        if 'element_electron_shells' in v:
            bse_shells = v['element_electron_shells']
            src_shells = src_el['element_electron_shells']
            new_shells = _replace_shell_data(bse_shells, src_shells)
        if 'element_ecp' in v:
            bse_pots = v['element_ecp']
            src_pots = src_el['element_ecp']
            new_pots = _replace_ecp_data(bse_pots, src_pots)

        # add to the replacement map
        for sh in new_shells:
            fpath = sh.pop('data_source')
            if not fpath in replace_map:
                replace_map[fpath] = {}
            if not k in replace_map[fpath]:
                replace_map[fpath][k] = {}
            if not 'element_electron_shells' in replace_map[fpath][k]:
                replace_map[fpath][k]['element_electron_shells'] = []
            replace_map[fpath][k]['element_electron_shells'].append(sh)

        for pot in new_pots:
            fpath = pot.pop('data_source')
            if not fpath in replace_map:
                replace_map[fpath] = {}
            if not k in replace_map[fpath]:
                replace_map[fpath][k] = {}
            if not 'element_ecp' in replace_map[fpath][k]:
                replace_map[fpath][k]['element_ecp'] = []
            replace_map[fpath][k]['element_ecp'].append(pot)

    # Actually do the replacements
    for fpath, replace_data in replace_map.items():

        # Read the original data from the file
        if fpath is not None:
            orig_data = read_json_basis(fpath)
        else:
            orig_data = {'basis_set_elements': {}}
            fpath = "MISSING.json"

        for el, replace_eldata in replace_data.items():
            if el in orig_data['basis_set_elements']:
                orig_eldata = orig_data['basis_set_elements'][el]

                # orig_eldata is the original data for an element
                # replace_eldata is what we are replacing with

                # Sort into the same order as orig data
                new_shell_order = []
                new_ecp_order = []
                at_shell_end = []
                at_ecp_end = []

                if 'element_electron_shells' in replace_eldata:
                    for sh1 in replace_eldata['element_electron_shells']:
                        for idx, sh2 in enumerate(orig_eldata['element_electron_shells']):
                            if compare_electron_shells(sh1, sh2, rel_tol=1e-3):
                                new_shell_order.append((idx, sh1))
                                break
                        else:
                            at_shell_end.append(sh1)

                if 'element_ecp' in replace_eldata:
                    for pot1 in replace_eldata['element_ecp']:
                        for idx, pot2 in enumerate(orig_eldata['element_ecp']):
                            if compare_ecp_pots(pot1, pot2, rel_tol=1e-3):
                                new_ecp_order.append((idx, pot1))
                                break
                        else:
                            at_ecp_end.append(pot1)

                if len(new_shell_order) > 0:
                    new_shell_order = sorted(new_shell_order)
                    new_shell_order = [x[1] for x in new_shell_order]
                    new_shell_order.extend(at_shell_end)
                    orig_eldata['element_electron_shells'] = new_shell_order

                if len(new_ecp_order) > 0:
                    new_ecp_order = sorted(new_ecp_order)
                    new_ecp_order = [x[1] for x in new_ecp_order]
                    new_ecp_order.extend(at_ecp_end)
                    orig_eldata['element_ecp'] = new_ecp_order
            else:
                orig_data['basis_set_elements'][el] = replace_eldata

        if not inplace:
            fpath = fpath + '.diff'

        write_json_basis(fpath, orig_data)

    print()
    print("     Not in src: ", _print_list(not_in_src))
    print("     Not in bse: ", _print_list(not_in_bse))
    print()

    return bse_data

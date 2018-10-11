'''
Functions for comparing basis sets and pieces of basis sets
'''

import operator
import copy
from .. import manip


def _reldiff(a, b):
    """
    Computes the relative difference of two floating-point numbers

    rel = abs(a-b)/min(abs(a), abs(b))

    If a == 0 and b == 0, then 0.0 is returned
    Otherwise if a or b is 0.0, inf is returned.
    """

    a = float(a)
    b = float(b)
    aa = abs(a)
    ba = abs(b)

    if a == 0.0 and b == 0.0:
        return 0.0
    elif a == 0 or b == 0.0:
        return float('inf')

    return abs(a - b) / min(aa, ba)


def _compare_keys(element1, element2, key, compare_func, *args):
    """
    Compares a specific key between two elements of a basis set

    If the key exists in one element but not the other, False is returned.

    If the key exists in neither element, True is returned.

    Parameters
    ----------
    element1 : dict
        Basis info for an element
    element2 : dict
        Basis info for another element
    key : string
        Key to compare in the two elements
    compare_func : function
        Function that returns True if the data under the key is equivalent
        in both elements
    args
        Additional arguments to be passed to compare_Func
    """
    if key in element1 and key in element2:
        if not compare_func(element1[key], element2[key], *args):
            return False
    elif key in element1 or key in element2:
        return False

    return True


def _compare_vector(arr1, arr2, rel_tol):
    """
    Compares two vectors (python lists) for approximate equality.

    Each array contains floats or strings convertible to floats

    This function returns True if both arrays are of the same length
    and each value is within the given relative tolerance.
    """

    length = len(arr1)
    if len(arr2) != length:
        return False

    for i in range(length):
        element_1 = float(arr1[i])
        element_2 = float(arr2[i])

        diff = abs(abs(element_1) - abs(element_2))
        if diff != 0.0:
            rel = _reldiff(element_1, element_2)

            # For a basis set, a relatively coarse comparison
            # should be acceptible
            if rel > rel_tol:
                return False

    return True


def _compare_matrix(mat1, mat2, rel_tol):
    """
    Compares two matrices (nested python lists) for approximate equality.

    Each matrix contains floats or strings convertible to floats

    This function returns True if both matrices are of the same dimensions
    and each value is within the given relative tolerance.
    """

    length = len(mat1)
    if len(mat2) != length:
        return False

    for i in range(length):
        if _compare_vector(mat1[i], mat2[i], rel_tol) is False:
            return False

    return True


def compare_electron_shells(shell1, shell2, compare_meta=False, rel_tol=0.0):
    '''
    Compare two electron shells for approximate equality
    (exponents/coefficients are within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''

    if shell1['shell_angular_momentum'] != shell2['shell_angular_momentum']:
        return False

    exponents1 = shell1['shell_exponents']
    exponents2 = shell2['shell_exponents']
    coefficients1 = shell1['shell_coefficients']
    coefficients2 = shell2['shell_coefficients']

    if not _compare_vector(exponents1, exponents2, rel_tol):
        return False
    if not _compare_matrix(coefficients1, coefficients2, rel_tol):
        return False
    if compare_meta:
        if shell1['shell_region'] != shell2['shell_region']:
            return False
        if shell1['shell_harmonic_type'] != shell2['shell_harmonic_type']:
            return False
        if shell1['shell_function_type'] != shell2['shell_function_type']:
            return False
        return True
    else:
        return True


def electron_shells_are_subset(subset, superset, compare_meta=False, rel_tol=0.0):
    '''
    Determine if a list of electron shells is a subset of another

    If 'subset' is a subset of the 'superset', True is returned.

    The shells are compared approximately (exponents/coefficients are 
    within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''
    for item1 in subset:
        for item2 in superset:
            if compare_electron_shells(item1, item2, compare_meta, rel_tol):
                break
        else:
            return False

    return True


def electron_shells_are_equal(shells1, shells2, compare_meta=False, rel_tol=0.0):
    '''
    Determine if a list of electron shells is the same as another

    The shells are compared approximately (exponents/coefficients are 
    within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''

    # Lists are equal if each is a subset of the other
    # Slow but effective
    return electron_shells_are_subset(shells1, shells2, compare_meta, rel_tol) and electron_shells_are_subset(
        shells2, shells1, compare_meta, rel_tol)


def compare_ecp_pots(potential1, potential2, compare_meta=False, rel_tol=0.0):
    '''
    Compare two ecp potentials for approximate equality
    (exponents/coefficients are within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''

    if potential1['potential_angular_momentum'] != potential2['potential_angular_momentum']:
        return False

    rexponents1 = potential1['potential_r_exponents']
    rexponents2 = potential2['potential_r_exponents']
    gexponents1 = potential1['potential_gaussian_exponents']
    gexponents2 = potential2['potential_gaussian_exponents']
    coefficients1 = potential1['potential_coefficients']
    coefficients2 = potential2['potential_coefficients']

    # integer comparison
    if rexponents1 != rexponents2:
        return False
    if not _compare_vector(gexponents1, gexponents2, rel_tol):
        return False
    if not _compare_matrix(coefficients1, coefficients2, rel_tol):
        return False
    if compare_meta:
        if potential1['potential_ecp_type'] != potential2['potential_ecp_type']:
            return False
        return True
    else:
        return True


def ecp_pots_are_subset(subset, superset, compare_meta=False, rel_tol=0.0):
    '''
    Determine if a list of ecp potentials is a subset of another

    If 'subset' is a subset of the 'superset', True is returned.

    The potentials are compared approximately (exponents/coefficients are 
    within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''

    for item1 in subset:
        for item2 in superset:
            if compare_ecp_pots(item1, item2, compare_meta, rel_tol):
                break
        else:
            return False

    return True


def ecp_pots_are_equal(pots1, pots2, compare_meta=False, rel_tol=0.0):
    '''
    Determine if a list of electron shells is the same as another

    The potentials are compared approximately (exponents/coefficients are 
    within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''

    # Lists are equal if each is a subset of the other
    # Slow but effective
    return ecp_pots_are_subset(pots1, pots2, compare_meta) and ecp_pots_are_subset(pots2, pots1, compare_meta)


def compare_elements(element1,
                     element2,
                     compare_electron_shells_meta=False,
                     compare_ecp_pots_meta=False,
                     compare_meta=False,
                     rel_tol=0.0):
    '''
    Determine if the basis information for two elements is the same as another

    Exponents/coefficients are compared using a tolerance.

    Parameters
    ----------
    element1 : dict
        Basis information for an element
    element2 : dict
        Basis information for another element
    compare_electron_shells_meta : bool
        Compare the metadata of electron shells
    compare_ecp_pots_meta : bool
        Compare the metadata of ECP potentials
    compare_meta : bool
        Compare the overall element metadata
    rel_tol : float
        Maximum relative error that is considered equal
    '''

    if not _compare_keys(element1, element2, 'element_electron_shells', electron_shells_are_equal,
                         compare_electron_shells_meta, rel_tol):
        return False

    if not _compare_keys(element1, element2, 'element_ecp', ecp_pots_are_equal, compare_ecp_pots_meta, rel_tol):
        return False

    if not _compare_keys(element1, element2, 'element_ecp_electrons', operator.eq):
        return False

    if compare_meta:
        if not _compare_keys(element1, element2, 'element_references', operator.eq):
            return False

    return True


def compare_basis(bs1,
                  bs2,
                  compare_electron_shells_meta=False,
                  compare_ecp_pots_meta=False,
                  compare_elements_meta=False,
                  compare_meta=False,
                  rel_tol=0.0):
    '''
    Determine if two basis set dictionaries are the same

    bs1 : dict
        Full basis information
    bs2 : dict
        Full basis information
    compare_electron_shells_meta : bool
        Compare the metadata of electron shells
    compare_ecp_pots_meta : bool
        Compare the metadata of ECP potentials
    compare_elements_meta : bool
        Compare the overall element metadata
    compare_meta: bool
        Compare the metadata for the basis set (name, description, etc)
    rel_tol : float
        Maximum relative error that is considered equal
    '''

    els1 = sorted(list(bs1['basis_set_elements'].keys()))
    els2 = sorted(list(bs2['basis_set_elements'].keys()))
    if not els1 == els2:
        return False

    for el in els1:
        if not compare_elements(
                bs1['basis_set_elements'][el],
                bs2['basis_set_elements'][el],
                compare_electron_shells_meta=compare_electron_shells_meta,
                compare_ecp_pots_meta=compare_ecp_pots_meta,
                compare_meta=compare_elements_meta,
                rel_tol=rel_tol):
            print("Elements failed: ", bs1['basis_set_name'], el)
            return False
    if compare_meta:
        for k in [
                'basis_set_name', 'basis_set_family', 'basis_set_description', 'basis_set_revision_description',
                'basis_set_role', 'basis_set_auxiliaries'
        ]:
            if not _compare_keys(bs1, bs2, k, operator.eq):
                return False
    return True


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

    shells1 = manip.sort_shells(s1)
    shells2 = manip.sort_shells(s2)

    for n in range(nsh):
        sh1 = shells1[n]
        sh2 = shells2[n]

        nprim = len(sh1['shell_exponents'])
        if len(sh2['shell_exponents']) != nprim:
            print("Different number of primitives for shell {}".format(n))
            return float('inf')

        ngen = len(sh1['shell_coefficients'])
        if len(sh2['shell_coefficients']) != ngen:
            print("Different number of general contractions for shell {}".format(n))
            return float('inf')

        for p in range(nprim):
            e1 = sh1['shell_exponents'][p]
            e2 = sh2['shell_exponents'][p]
            r = _reldiff(e1, e2)
            if r > 0.0:
                print("   Exponent {:3}: {:20} {:20} -> {:16.8e}".format(p, e1, e2, r))
            max_rdiff = max(max_rdiff, r)

            for g in range(ngen):
                c1 = sh1['shell_coefficients'][g][p]
                c2 = sh2['shell_coefficients'][g][p]
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

    pots1 = manip.sort_potentials(p1)
    pots2 = manip.sort_potentials(p2)

    for n in range(np):
        pot1 = pots1[n]
        pot2 = pots2[n]

        nprim = len(pot1['potential_gaussian_exponents'])
        if len(pot2['potential_gaussian_exponents']) != nprim:
            print("Different number of primitives for potential {}".format(n))
            return float('inf')

        ngen = len(pot1['potential_coefficients'])
        if len(pot2['potential_coefficients']) != ngen:
            print("Different number of general contractions for potential {}".format(n))
            return float('inf')

        for p in range(nprim):
            e1 = pot1['potential_gaussian_exponents'][p]
            e2 = pot2['potential_gaussian_exponents'][p]
            r = _reldiff(e1, e2)
            if r > 0.0:
                print("   Gaussian Exponent {:3}: {:20} {:20} -> {:16.8e}".format(p, e1, e2, r))

            e1 = pot1['potential_r_exponents'][p]
            e2 = pot2['potential_r_exponents'][p]
            r = _reldiff(e1, e2)
            if r > 0.0:
                print("          R Exponent {:3}: {:20} {:20} -> {:16.8e}".format(p, e1, e2, r))
            max_rdiff = max(max_rdiff, r)

            for g in range(ngen):
                c1 = pot1['potential_coefficients'][g][p]
                c2 = pot2['potential_coefficients'][g][p]
                r = _reldiff(c1, c2)
                if r > 0.0:
                    print("         Coefficient {:3}: {:20} {:20} -> {:16.8e}".format(p, c1, c2, r))
                max_rdiff = max(max_rdiff, r)

    print()
    print("Max relative difference for these potentials: {}".format(max_rdiff))
    return max_rdiff


def subtract_electron_shells(s1, s2, rel_tol=0.0):
    """
    Returns the difference between two lists of electron shells (s1 - s2)

    This will remove any shells from s1 that are also in s2, within a tolerance
    """

    diff_shells = []
    for sh1 in s1:
        for sh2 in s2:
            if compare_electron_shells(sh1, sh2, rel_tol=rel_tol):
                break
        else:
            diff_shells.append(copy.deepcopy(sh1))

    return diff_shells

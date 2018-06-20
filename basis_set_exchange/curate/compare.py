'''
Functions for comparing basis sets and pieces of basis sets
'''

import operator


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


def _compare_vector(arr1, arr2):
    """
    Compares two vectors (python lists) for approximate equality.

    Each array contains floats or strings convertible to floats

    This function returns True if both arrays are of the same length
    and each value is approximately equal.
    """

    length = len(arr1)
    if len(arr2) != length:
        return False

    for i in range(length):
        element_1 = float(arr1[i])
        element_2 = float(arr2[i])

        diff = abs(abs(element_1) - abs(element_2))
        if diff != 0.0:
            rel = diff / min(abs(element_1), abs(element_2))

            # For a basis set, a relatively coarse comparison
            # should be acceptible
            if rel > 1.0e-10:
                return False

    return True


def _compare_matrix(mat1, mat2):
    """
    Compares two matrices (nested python lists) for approximate equality.

    Each matrix contains floats or strings convertible to floats

    This function returns True if both matrices are of the same dimensions
    and each value is approximately equal.
    """

    length = len(mat1)
    if len(mat2) != length:
        return False

    for i in range(length):
        if _compare_vector(mat1[i], mat2[i]) is False:
            return False

    return True


def compare_electron_shells(shell1, shell2, compare_meta=False):
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

    if not _compare_vector(exponents1, exponents2):
        return False
    if not _compare_matrix(coefficients1, coefficients2):
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


def electron_shells_are_subset(subset, superset, compare_meta=False):
    '''
    Determine if a list of electron shells is a subset of another

    If 'subset' is a subset of the 'superset', True is returned.

    The shells are compared approximately (exponents/coefficients are 
    within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''
    for item1 in subset:
        for item2 in superset:
            if compare_electron_shells(item1, item2, compare_meta):
                break
        else:
            return False

    return True


def electron_shells_are_equal(shells1, shells2, compare_meta=False):
    '''
    Determine if a list of electron shells is the same as another

    The shells are compared approximately (exponents/coefficients are 
    within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''

    # Lists are equal if each is a subset of the other
    # Slow but effective
    return electron_shells_are_subset(shells1, shells2, compare_meta) and electron_shells_are_subset(
        shells2, shells1, compare_meta)


def compare_ecp_pots(potential1, potential2, compare_meta=False):
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
    if not _compare_vector(gexponents1, gexponents2):
        return False
    if not _compare_matrix(coefficients1, coefficients2):
        return False
    if compare_meta:
        if potential1['potential_ecp_type'] != potential2['potential_ecp_type']:
            return False
        return True
    else:
        return True


def ecp_pots_are_subset(subset, superset, compare_meta=False):
    '''
    Determine if a list of ecp potentials is a subset of another

    If 'subset' is a subset of the 'superset', True is returned.

    The potentials are compared approximately (exponents/coefficients are 
    within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality. 
    '''

    for item1 in subset:
        for item2 in superset:
            if compare_ecp_pots(item1, item2, compare_meta):
                break
        else:
            return False

    return True


def ecp_pots_are_equal(pots1, pots2, compare_meta=False):
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
                     compare_meta=False):
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
    '''

    if not _compare_keys(element1, element2, 'element_electron_shells', electron_shells_are_equal,
                         compare_electron_shells_meta):
        return False

    if not _compare_keys(element1, element2, 'element_ecp', ecp_pots_are_equal, compare_ecp_pots_meta):
        return False

    if not _compare_keys(element1, element2, 'element_ecp_electrons', operator.eq):
        return False

    if compare_meta:
        if not _compare_keys(element1, element2, 'element_references', operator.eq):
            return False

    return True

# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''
Functions for comparing basis sets and pieces of basis sets
'''

import operator
from ..sort import sort_shell


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
            # should be acceptable
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
        if not _compare_vector(mat1[i], mat2[i], rel_tol):
            return False

    return True


def compare_electron_shells(shell1, shell2, compare_meta=False, rel_tol=0.0):
    '''
    Compare two electron shells for approximate equality
    (exponents/coefficients are within a tolerance)

    If compare_meta is True, the metadata is also compared for exact equality.
    '''

    if shell1['angular_momentum'] != shell2['angular_momentum']:
        return False

    # Sort into some canonical order
    shell1 = sort_shell(shell1)
    shell2 = sort_shell(shell2)

    # Zip together exponents and coeffs
    # This basically creates the typical matrix with exponents
    # being in the first column
    tmp1 = list(zip(shell1['exponents'], *shell1['coefficients']))
    tmp2 = list(zip(shell2['exponents'], *shell2['coefficients']))

    if not _compare_matrix(tmp1, tmp2, rel_tol):
        return False
    if compare_meta:
        if shell1['region'] != shell2['region']:
            return False
        if shell1['function_type'] != shell2['function_type']:
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

    if len(shells1) != len(shells2):
        return False

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

    if potential1['angular_momentum'] != potential2['angular_momentum']:
        return False

    rexponents1 = potential1['r_exponents']
    rexponents2 = potential2['r_exponents']
    gexponents1 = potential1['gaussian_exponents']
    gexponents2 = potential2['gaussian_exponents']
    coefficients1 = potential1['coefficients']
    coefficients2 = potential2['coefficients']

    # integer comparison
    if rexponents1 != rexponents2:
        return False
    if not _compare_vector(gexponents1, gexponents2, rel_tol):
        return False
    if not _compare_matrix(coefficients1, coefficients2, rel_tol):
        return False
    if compare_meta:
        if potential1['ecp_type'] != potential2['ecp_type']:
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

    if not _compare_keys(element1, element2, 'electron_shells', electron_shells_are_equal,
                         compare_electron_shells_meta, rel_tol):
        return False

    if not _compare_keys(element1, element2, 'ecp_potentials', ecp_pots_are_equal, compare_ecp_pots_meta, rel_tol):
        return False

    if not _compare_keys(element1, element2, 'ecp_electrons', operator.eq):
        return False

    if compare_meta:
        if not _compare_keys(element1, element2, 'references', operator.eq):
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

    els1 = sorted(bs1['elements'].keys())
    els2 = sorted(bs2['elements'].keys())
    if not els1 == els2:
        return False

    for el in els1:
        if not compare_elements(bs1['elements'][el],
                                bs2['elements'][el],
                                compare_electron_shells_meta=compare_electron_shells_meta,
                                compare_ecp_pots_meta=compare_ecp_pots_meta,
                                compare_meta=compare_elements_meta,
                                rel_tol=rel_tol):
            print("Element failed:", el)
            return False
    if compare_meta:
        for k in ['name', 'family', 'description', 'revision_description', 'role', 'auxiliaries']:
            if not _compare_keys(bs1, bs2, k, operator.eq):
                return False
    return True

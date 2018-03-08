import operator

def _compare_keys(element1, element2, key, compare_func, *args):
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
        if _compare_vector(mat1[i], mat2[i]) == False:
            return False

    return True
         

def compare_shells(shell1, shell2, compare_meta=False):
    if shell1['shellAngularMomentum'] != shell2['shellAngularMomentum']:
        return False

    exponents1 = shell1['shellExponents']
    exponents2 = shell2['shellExponents']
    coefficients1 = shell1['shellCoefficients']
    coefficients2 = shell2['shellCoefficients']

    if not _compare_vector(exponents1, exponents2):
        return False
    if not _compare_matrix(coefficients1, coefficients2):
        return False
    if compare_meta:
        if shell1['shellRegion'] != shell2['shellRegion']:
            return False
        if shell1['shellHarmonicType'] != shell2['shellHarmonicType']:
            return False
        if shell1['shellFunctionType'] != shell2['shellFunctionType']:
            return False
        return True
    else:
        return True


def shells_are_subset(subset, superset, compare_meta=False):
    for item1 in subset:
        for item2 in superset:
            if compare_shells(item1, item2, compare_meta):
                break
        else:
            return False

    return True


def shells_are_equal(shells1, shells2, compare_meta=False):
    # Slow but effective
    return shells_are_subset(shells1, shells2, compare_meta) and shells_are_subset(shells2, shells1, compare_meta)


def compare_ecp_pots(potential1, potential2, compare_meta=False):
    if potential1['potentialAngularMomentum'] != potential2['potentialAngularMomentum']:
        return False

    rexponents1 = potential1['potentialRExponents']
    rexponents2 = potential2['potentialRExponents']
    gexponents1 = potential1['potentialGaussianExponents']
    gexponents2 = potential2['potentialGaussianExponents']
    coefficients1 = potential1['potentialCoefficients']
    coefficients2 = potential2['potentialCoefficients']

    # integer comparison
    if rexponents1 != rexponents2:
        return False
    if not _compare_vector(gexponents1, gexponents2):
        return False
    if not _compare_matrix(coefficients1, coefficients2):
        return False
    if compare_meta:
        if potential1['potentialECPType'] != potential2['potentialECPType']:
            return False
        return True
    else:
        return True


def ecp_pots_are_subset(subset, superset, compare_meta=False):
    for item1 in subset:
        for item2 in superset:
            if compare_ecp_pots(item1, item2, compare_meta):
                break
        else:
            return False

    return True


def ecp_pots_are_equal(pots1, pots2, compare_meta=False):
    # Slow but effective
    return ecp_pots_are_subset(pots1, pots2, compare_meta) and ecp_pots_are_subset(pots2, pots1, compare_meta)


def compare_elements(element1, element2, compare_shells_meta=False,
                     compare_ecp_pots_meta=False, compare_meta=False):
    if not _compare_keys(element1, element2, 'elementElectronShells',
                        shells_are_equal, compare_shells_meta):
        return False

    if not _compare_keys(element1, element2, 'elementECP',
                        ecp_pots_are_equal, compare_ecp_pots_meta):
        return False; 

    if not _compare_keys(element1, element2, 'elementECPElectrons', operator.eq):
        return False; 


    if compare_meta:
        if not _compare_keys(element1, element2, 'elementReferences',
                            shells_are_equal, operator.eq):
            return False

    return True

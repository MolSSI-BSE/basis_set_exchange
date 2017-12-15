import operator
import numpy as np


def _compare_keys(element1, element2, key, compare_func, *args):
    if key in element1 and key in element2:
        if not compare_func(element1[key], element2[key], *args):
            return False
    elif key in element1 or key in element2:
        return False

    return True


def compare_shells(shell1, shell2, compare_meta=False):
    if shell1['shellAngularMomentum'] != shell2['shellAngularMomentum']:
        return False

    exponents1 = shell1['shellExponents']
    exponents2 = shell2['shellExponents']
    coefficients1 = shell1['shellCoefficients']
    coefficients2 = shell2['shellCoefficients']

    exponents1 = np.array(exponents1).astype(np.float)
    exponents2 = np.array(exponents2).astype(np.float)
    coefficients1 = np.array(coefficients1).astype(np.float)
    coefficients2 = np.array(coefficients2).astype(np.float)

    if exponents1.shape != exponents2.shape:
        return False
    if coefficients1.shape != coefficients2.shape:
        return False
    if not np.allclose(exponents1, exponents2, rtol=1e-10):
        return False
    if not np.allclose(coefficients1, coefficients2, rtol=1e-10):
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

    rexponents1 = np.array(rexponents1).astype(np.int)
    rexponents2 = np.array(rexponents2).astype(np.int)
    gexponents1 = np.array(gexponents1).astype(np.float)
    gexponents2 = np.array(gexponents2).astype(np.float)
    coefficients1 = np.array(coefficients1).astype(np.float)
    coefficients2 = np.array(coefficients2).astype(np.float)

    if rexponents1.shape != rexponents2.shape:
        return False
    if gexponents1.shape != gexponents2.shape:
        return False
    if coefficients1.shape != coefficients2.shape:
        return False
    if not np.alltrue(rexponents1 == rexponents2):
        return False
    if not np.allclose(gexponents1, gexponents2, rtol=1e-10):
        return False
    if not np.allclose(coefficients1, coefficients2, rtol=1e-10):
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

import numpy as np

def compare_shell(shell1, shell2, compare_meta=False):
    if shell1['shellAngularMomentum'] != shell2['shellAngularMomentum']:
        return False

    # Replace fortran-style 'D' with 'E'
    exponents1 = [ x.replace('D', 'E') for x in shell1['shellExponents'] ]
    exponents2 = [ x.replace('D', 'E') for x in shell2['shellExponents'] ]
    coefficients1 = [ [ x.replace('D', 'E') for x in y ] for y in shell1['shellCoefficients'] ]
    coefficients2 = [ [ x.replace('D', 'E') for x in y ] for y in shell2['shellCoefficients'] ]

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
            if compare_shell(item1, item2, compare_meta):
                break
        else:
            return False

    return True


def shells_are_equal(shells1, shells2, compare_meta=False):
    # Slow but effective
    return shells_are_subset(shells1, shells2, compare_meta) and shells_are_subset(shells2, shells1, compare_meta)


def compare_ecp_pot(potential1, potential2, compare_meta=False):
    if potential1['potentialAngularMomentum'] != potential2['potentialAngularMomentum']:
        return False

    # Replace fortran-style 'D' with 'E'
    gexponents1 = [ x.replace('D', 'E') for x in potential1['potentialGaussianExponents'] ]
    gexponents2 = [ x.replace('D', 'E') for x in potential2['potentialGaussianExponents'] ]
    coefficients1 = [ [ x.replace('D', 'E') for x in y ] for y in potential1['potentialCoefficients'] ]
    coefficients2 = [ [ x.replace('D', 'E') for x in y ] for y in potential2['potentialCoefficients'] ]

    rexponents1 = np.array(potential1['potentialRExponents']).astype(np.int)
    rexponents2 = np.array(potential2['potentialRExponents']).astype(np.int)
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
            if compare_ecp_pot(item1, item2, compare_meta):
                break
        else:
            return False

    return True
    

def ecp_pots_are_equal(pots1, pots2, compare_meta=False):
    # Slow but effective
    return ecp_pots_are_subset(pots1, pots2, compare_meta) and ecp_pots_are_subset(pots2, pots1, compare_meta)


def compare_element(element1, element2, compare_shell_meta=False, compare_ecp_pots_meta=False, compare_meta=False):

    if 'elementElectronShells' in element1 and 'elementElectronShells' in element2:
        if not shells_are_equal(element1['elementElectronShells'], element2['elementElectronShells'], compare_shell_meta):
            return False
    elif 'elementElectronShells' in element1 or 'elementElectronShells' in element2:
        return False


    if 'elementECPElectrons' in element1 and 'elementECPElectrons' in element2:
        if element1['elementECPElectrons'] != element2['elementECPElectrons']:
            return False
    elif 'elementECPElectrons' in element1 and 'elementECPElectrons' in element2:
        return False
    
    if 'elementECP' in element1 and 'elementECP' in element2:
        if not ecp_pots_are_equal(element1['elementECP'], element2['elementECP'], compare_ecp_pots_meta):
            return False
    elif 'elementECP' in element1 or 'elementECP' in element2:
        return False

    if compare_meta:
        if 'elementReferences' in element1 and 'elementReferences' in element2:
            if element1['elementReferences'] != element2['elementReferences']:
                return False
        elif 'elementReferences' in element1 or 'elementReferences' in element2:
            return False

    return True

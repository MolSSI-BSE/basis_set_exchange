"""
Common basis set manipulations (such as uncontracting)
"""

import json
import os
import copy
from . import lut


def contraction_string(element):
    """
    Forms a string specifying the contractions for an element

    ie, (16s,10p) -> [4s,3p]
    """

    if 'elementElectronShells' not in element:
        return ""

    cont_map = dict()
    for sh in element['elementElectronShells']:
        nprim = len(sh['shellExponents'])
        ngeneral = len(sh['shellCoefficients'])

        # is a combined general contraction (sp, spd, etc)
        is_spdf = len(sh['shellAngularMomentum']) > 1

        for am in sh['shellAngularMomentum']:
            # If this a general contraction (and not combined am), then use that
            ncont = ngeneral if not is_spdf else 1

            if am not in cont_map:
                cont_map[am] = (nprim, ncont)
            else:
                cont_map[am] = (cont_map[am][0] + nprim, cont_map[am][1] + ncont)

    primstr = ""
    contstr = ""
    for am in sorted(cont_map.keys()):
        nprim, ncont = cont_map[am]

        if am != 0:
            primstr += ','
            contstr += ','
        primstr += str(nprim) + lut.amint_to_char([am])
        contstr += str(ncont) + lut.amint_to_char([am])

    return "({}) -> [{}]".format(primstr, contstr)


def check_compatible_merge(dest, source):
    """
    TODO - check for any incompatibilities between the two elements
    """
    pass


def merge_element_data(dest, sources):
    """
    Merges the basis set data for an element from multiple sources
    into dest.

    The destination is not modified
    """

    # return a shallow copy
    ret = dest.copy()

    for s in sources:
        check_compatible_merge(dest, s)

        if 'elementElectronShells' in s:
            if 'elementElectronShells' not in ret:
                ret['elementElectronShells'] = []
            ret['elementElectronShells'].extend(s['elementElectronShells'])
        if 'elementECP' in s:
            if 'elementECP' in ret:
                raise RuntimeError('Cannot overwrite existing ECP')
            ret['elementECP'] = s['elementECP']
            ret['elementECPElectrons'] = s['elementECPElectrons']
        if 'elementReferences' in s:
            if 'elementReferences' not in ret:
                ret['elementReferences'] = []
            for ref in s['elementReferences']:
                if not ref in ret['elementReferences']:
                    ret['elementReferences'].append(ref)

    # Sort the shells by angular momentum
    ret['elementElectronShells'].sort(key=lambda x: x['shellAngularMomentum'])

    return ret


def prune_basis(basis):
    """
    Removes primitives that have a zero coefficient, and
    removes duplicate shells

    This only finds EXACT duplicates, and is meant to be used
    after uncontracting
    """

    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basisSetElements'].items():
        for sh in el['elementElectronShells']:

            new_exponents = []
            new_coefficients = []

            exponents = sh['shellExponents']

            # transpose of the coefficient matrix
            coeff_t = list(map(list, zip(*sh['shellCoefficients'])))

            # only add if there is a nonzero contraction coefficient
            for i in range(len(sh['shellExponents'])):
                if not all([float(x) == 0.0 for x in coeff_t[i]]):
                    new_exponents.append(exponents[i])
                    new_coefficients.append(coeff_t[i])

            # take the transpose again, putting the general contraction
            # as the slowest index
            new_coefficients = list(map(list, zip(*new_coefficients)))

            # only add if there isn't a duplicate
            sh['shellExponents'] = new_exponents
            sh['shellCoefficients'] = new_coefficients

        # Remove any duplicates
        shells = el['elementElectronShells']
        el['elementElectronShells'] = []

        for sh in shells:
            if sh not in el['elementElectronShells']:
                el['elementElectronShells'].append(sh)

    return new_basis


def uncontract_spdf(basis):
    """
    Removes sp, spd, spdf, etc, contractions from a basis set

    The general contractions are replaced by uncontracted versions

    The input basis set is not modified.
    """

    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basisSetElements'].items():
        newshells = []

        for sh in el['elementElectronShells']:

            # am will be a list
            am = sh['shellAngularMomentum']

            # if this is an sp, spd,...  orbital
            if len(am) > 1:
                for i, c in enumerate(sh['shellCoefficients']):
                    newsh = sh.copy()
                    newsh['shellAngularMomentum'] = [am[i]]
                    newsh['shellCoefficients'] = [c]
                    newshells.append(newsh)
            else:
                newshells.append(sh)

        el['elementElectronShells'] = newshells

    return prune_basis(new_basis)


def uncontract_general(basis):
    """
    Removes the general contractions from a basis set

    The input basis set is not modified
    """

    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basisSetElements'].items():
        newshells = []

        for sh in el['elementElectronShells']:
            # Don't uncontract sp, spd,.... orbitals
            # leave that to uncontract_spdf
            if len(sh['shellAngularMomentum']) == 1:
                for c in sh['shellCoefficients']:
                    # copy, them replace 'shellCoefficients'
                    newsh = sh.copy()
                    newsh['shellCoefficients'] = [c]
                    newshells.append(newsh)
            else:
                newshells.append(sh)

        el['elementElectronShells'] = newshells

    return prune_basis(new_basis)


def uncontract_segmented(basis):
    """
    Removes the segmented contractions from a basis set

    The input basis set is not modified
    """

    # This implicitly removes general contractions as well
    # But will leave sp, spd, orbitals alone
    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basisSetElements'].items():
        newshells = []

        for sh in el['elementElectronShells']:
            exponents = sh['shellExponents']
            coefficients = sh['shellCoefficients']
            nam = len(sh['shellAngularMomentum'])

            for i in range(len(sh['shellExponents'])):
                newsh = sh.copy()
                newsh['shellExponents'] = [exponents[i]]
                newsh['shellCoefficients'] = [["1.00000000"] * nam]

                # Remember to transpose the coefficients
                newsh['shellCoefficients'] = list(map(list, zip(*newsh['shellCoefficients'])))

                newshells.append(newsh)

        el['elementElectronShells'] = newshells

    return new_basis

"""
Common basis set manipulations

This module contains functions for uncontracting and merging basis set
data, as well as some other small functions.
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

    # Does not have electron shells (ECP only?)
    if 'element_electron_shells' not in element:
        return ""

    cont_map = dict()
    for sh in element['element_electron_shells']:
        nprim = len(sh['shell_exponents'])
        ngeneral = len(sh['shell_coefficients'])

        # is a combined general contraction (sp, spd, etc)
        is_spdf = len(sh['shell_angular_momentum']) > 1

        for am in sh['shell_angular_momentum']:
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


def merge_element_data(dest, sources):
    """
    Merges the basis set data for an element from multiple sources
    into dest.

    The destination is not modified, and a (shallow) copy of dest is returned
    with the data from sources added.
    """

    ret = dest.copy()

    for s in sources:
        if 'element_electron_shells' in s:
            if 'element_electron_shells' not in ret:
                ret['element_electron_shells'] = []
            ret['element_electron_shells'].extend(s['element_electron_shells'])
        if 'element_ecp' in s:
            if 'element_ecp' in ret:
                raise RuntimeError('Cannot overwrite existing ECP')
            ret['element_ecp'] = s['element_ecp']
            ret['element_ecp_electrons'] = s['element_ecp_electrons']
        if 'element_references' in s:
            if 'element_references' not in ret:
                ret['element_references'] = []
            for ref in s['element_references']:
                if not ref in ret['element_references']:
                    ret['element_references'].append(ref)

    # Sort the shells by angular momentum
    # Note that I don't sort ECP - ECP can't be composed, and
    # it should be sorted in the only source with ECP
    if 'element_electron_shells' in ret:
        ret['element_electron_shells'].sort(key=lambda x: x['shell_angular_momentum'])

    return ret


def prune_basis(basis):
    """
    Removes primitives that have a zero coefficient, and
    removes duplicate shells

    This only finds EXACT duplicates, and is meant to be used
    after uncontracting

    The input basis set is not modified.
    """

    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basis_set_elements'].items():
        if not 'element_electron_shells' in el:
            continue

        for sh in el['element_electron_shells']:
            new_exponents = []
            new_coefficients = []

            exponents = sh['shell_exponents']

            # transpose of the coefficient matrix
            coeff_t = list(map(list, zip(*sh['shell_coefficients'])))

            # only add if there is a nonzero contraction coefficient
            for i in range(len(sh['shell_exponents'])):
                if not all([float(x) == 0.0 for x in coeff_t[i]]):
                    new_exponents.append(exponents[i])
                    new_coefficients.append(coeff_t[i])

            # take the transpose again, putting the general contraction
            # as the slowest index
            new_coefficients = list(map(list, zip(*new_coefficients)))

            sh['shell_exponents'] = new_exponents
            sh['shell_coefficients'] = new_coefficients

        # Remove any duplicates
        shells = el.pop('element_electron_shells')
        el['element_electron_shells'] = []

        for sh in shells:
            if sh not in el['element_electron_shells']:
                el['element_electron_shells'].append(sh)

    return new_basis


def uncontract_spdf(basis):
    """
    Removes sp, spd, spdf, etc, contractions from a basis set

    The general contractions are replaced by uncontracted versions

    The input basis set is not modified, and any primitives with all
    zero coefficients are removed
    """

    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basis_set_elements'].items():

        if not 'element_electron_shells' in el:
            continue
        newshells = []

        for sh in el['element_electron_shells']:

            # am will be a list
            am = sh['shell_angular_momentum']

            # if this is an sp, spd,...  orbital
            if len(am) > 1:
                for i, c in enumerate(sh['shell_coefficients']):
                    newsh = sh.copy()
                    newsh['shell_angular_momentum'] = [am[i]]
                    newsh['shell_coefficients'] = [c]
                    newshells.append(newsh)
            else:
                newshells.append(sh)

        el['element_electron_shells'] = newshells

    return prune_basis(new_basis)


def uncontract_general(basis):
    """
    Removes the general contractions from a basis set

    The input basis set is not modified, and any primitives with all
    zero coefficients are removed
    """

    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basis_set_elements'].items():

        if not 'element_electron_shells' in el:
            continue

        newshells = []

        for sh in el['element_electron_shells']:
            # Don't uncontract sp, spd,.... orbitals
            # leave that to uncontract_spdf
            if len(sh['shell_angular_momentum']) == 1:
                for c in sh['shell_coefficients']:
                    # copy, them replace 'shell_coefficients'
                    newsh = sh.copy()
                    newsh['shell_coefficients'] = [c]
                    newshells.append(newsh)
            else:
                newshells.append(sh)

        el['element_electron_shells'] = newshells

    return prune_basis(new_basis)


def uncontract_segmented(basis):
    """
    Removes the segmented contractions from a basis set

    The input basis set is not modified
    """

    # This implicitly removes general contractions as well
    # But will leave sp, spd, orbitals alone
    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basis_set_elements'].items():

        if not 'element_electron_shells' in el:
            continue

        newshells = []

        for sh in el['element_electron_shells']:
            exponents = sh['shell_exponents']
            coefficients = sh['shell_coefficients']
            nam = len(sh['shell_angular_momentum'])

            for i in range(len(sh['shell_exponents'])):
                newsh = sh.copy()
                newsh['shell_exponents'] = [exponents[i]]
                newsh['shell_coefficients'] = [["1.00000000"] * nam]

                # Remember to transpose the coefficients
                newsh['shell_coefficients'] = list(map(list, zip(*newsh['shell_coefficients'])))

                newshells.append(newsh)

        el['element_electron_shells'] = newshells

    return new_basis


def transform_basis_name(name):
    """
    Transforms the name of a basis set to an internal representation

    This makes comparison of basis set names easier by, for example,
    converting the name to all lower case.
    """

    return name.lower()

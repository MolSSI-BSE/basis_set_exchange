'''
Common basis set manipulations (such as uncontracting)
'''

import json
import os
import copy
from . import io


def prune_zero_coefficients(basis):
    '''Removes primitives that have a zero coefficient
    '''

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
                if not all([ float(x) == 0.0 for x in coeff_t[i] ]):
                    new_exponents.append(exponents[i])
                    new_coefficients.append(coeff_t[i])

            # take the transpose again, putting the general contraction
            # as the slowest index
            new_coefficients = list(map(list, zip(*new_coefficients)))

            sh['shellExponents'] = new_exponents 
            sh['shellCoefficients'] = new_coefficients 

    return new_basis


def uncontract_spdf(basis):
    '''Removes sp, spd, spdf, etc, contractions from a basis set
    '''

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

    return prune_zero_coefficients(new_basis)


def uncontract_general(basis):
    '''Removes the general contractions from a basis set
    '''

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

    return prune_zero_coefficients(new_basis)


def uncontract_segmented(basis):
    '''Removes the segmented contractions from a basis set
    '''

    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basisSetElements'].items():
        newshells = []

        for sh in el['elementElectronShells']:
            exponents = sh['shellExponents']
            coefficients = sh['shellCoefficients']

            for i in range(len(sh['shellExponents'])):
                newsh = sh.copy()
                newsh['shellExponents'] = [exponents[i]]
                newsh['shellCoefficients'] = [ [c[i] for c in coefficients] ]

                # Remember to transpose the coefficients
                newsh['shellCoefficients'] = list(map(list, zip(*newsh['shellCoefficients']))) 

                newshells.append(newsh)

        el['elementElectronShells'] = newshells

    return new_basis 

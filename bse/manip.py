'''
Common basis set manipulations (such as uncontracting)
'''

import json
import os
import copy
from . import io


def merge_element_dict(parent, child):
    '''
    '''
    new_dict = copy.deepcopy(parent)
    for k, v in child.items():
        if not k in new_dict:
            new_dict[k] = v
        elif isinstance(v, list):
            new_dict[k].extend[v]
        elif isinstance(v, dict):
            new_dict[k] = merge_element_dict(new_dict[k], v)
        else:
            raise RuntimeError("Error merging type {}".format(type(v)))
    return new_dict


def prune_zero_coefficients(basis):
    '''Removes primitives that have a zero coefficient
    '''

    new_basis = copy.deepcopy(basis)

    for k, el in new_basis['basisSetElements'].items():
        for sh in el['elementElectronShells']:

            new_exponents = []
            new_coefficients = []

            # transpose of the coefficient matrix
            coeff_t = list(map(list, zip(*sh['shellCoefficients'])))

            for i in range(len(sh['shellExponents'])):
                if not all([ float(x) == 0.0 for x in coeff_t[i] ]):
                    new_exponents.append(sh['shellExponents'][i])
                    new_coefficients.append(coeff_t[i])

            # take the transpose again
            new_coefficients = list(map(list, zip(*new_coefficients)))

            sh['shellExponents'] = new_exponents 
            sh['shellCoefficients'] = new_coefficients 

    return new_basis


def uncontract_spdf(basis):
    '''Removes sp, spd, spdf, etc, contractions from a basis set
    '''

    new_basis = copy.deepcopy(basis)

    for k, el in basis['basisSetElements'].items():
        newshells = []

        for sh in el['elementElectronShells']:
            if len(sh['shellAngularMomentum']) > 1:
                for i, c in enumerate(sh['shellCoefficients']):
                    newsh = copy.deepcopy(sh)
                    newsh['shellAngularMomentum'] = [sh['shellAngularMomentum'][i]]
                    newsh['shellCoefficients'] = [c]
                    newshells.append(newsh)
            else:
                newshells.append(sh)

            new_basis['basisSetElements'][k]['elementElectronShells'] = newshells

    return prune_zero_coefficients(new_basis)


def uncontract_general(basis):
    '''Removes the general contractions from a basis set
    '''

    new_basis = copy.deepcopy(basis)

    for k, el in basis['basisSetElements'].items():
        newshells = []

        for sh in el['elementElectronShells']:
            if len(sh['shellAngularMomentum']) == 1:
                for c in sh['shellCoefficients']:
                    newsh = {k: v for k, v in sh.items() if k != 'shellCoefficients'}
                    newsh['shellCoefficients'] = [c]
                    newshells.append(newsh)
            else:
                newshells.append(sh)

            new_basis['basisSetElements'][k]['elementElectronShells'] = newshells

    return prune_zero_coefficients(new_basis)


def uncontract_segmented(basis):
    '''Removes the segmented contractions from a basis set
    '''

    new_basis = copy.deepcopy(basis)

    for k, el in basis['basisSetElements'].items():
        newshells = []

        for sh in el['elementElectronShells']:
            for i in range(len(sh['shellExponents'])):
                newsh = {k: v for k, v in sh.items()}

                newsh['shellExponents'] = [sh['shellExponents'][i]]
                newsh['shellCoefficients'] = []

                for c in range(len(sh['shellCoefficients'])):
                    newsh['shellCoefficients'].append([sh['shellCoefficients'][c][i]])
                newshells.append(newsh)

            new_basis['basisSetElements'][k]['elementElectronShells'] = newshells

    return new_basis 


#def validate_basis(basis):
#    #req_keys = ['name', 'version', 'elements']
#    req_keys = []
#    for k in req_keys:
#        if k not in basis:
#            raise RuntimeError('Missing key '.format(k))
#
#    for el, v in basis['elements'].items():
#        for sh in v['shells']:
#            # if this is combined AM, then the number of general contractions
#            # must equal the number of AM
#            n_am = len(sh['angularMomentum'])
#            n_gen = len(sh['coefficients'])
#            n_prim = len(sh['exponents'])
#
#            if n_am > 1 and n_gen != n_am:
#                raise RuntimeError('Number of general contractions ({}) not '
#                                   'compatible with AM={}'.format(n_gen, sh['angularMomentum']))
#
#            for g in sh['coefficients']:
#                if len(g) != n_prim:
#                    raise RuntimeError('Inconsistent number of primitives for general contraction.\n'
#                                       'Expected {}, got {}. Coefficients are: {} '.format(n_prim, len(g), g))

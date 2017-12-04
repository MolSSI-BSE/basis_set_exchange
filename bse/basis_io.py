'''
Functions for reading and writing the standard JSON-based
basis set format
'''

import json
import os
import copy
import collections

my_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(my_path)
bs_data_path = os.path.join(parent_path, 'basis')


def sort_basis_dict(bs):
    '''Sorts a basis set dictionary into a standard order

    This allows the written file to be more easily read by humans by,
    for example, putting the name and description before more detailed fields
    '''

    keyorder = ['basisSetName',
                'basisSetDescription',
                'basisSetRole',
                'basisSetRegion', 
                'basisSetElements',

                'elementReference',
                'elementElectronShells',
                'elementComponents',
                'elementEntry',

                'shellFunctionType',
                'shellHarmonicType',
                'shellAngularMomentum',
                'shellExponents',
                'shellCoefficients'
                
                ]

    # Add integers for the elements
    keyorder.extend(list(range(150)))

    bs_sorted = sorted(bs.items(), key=lambda x: keyorder.index(x[0]))
    bs_sorted = collections.OrderedDict(bs_sorted)

    for k,v in bs_sorted.items():
        if isinstance(v, dict):
            bs_sorted[k] = sort_basis_dict(v)
        elif k == 'elementElectronShells':
            bs_sorted[k] = [ sort_basis_dict(x) for x in v ]

    return bs_sorted


def read_json_basis_file(filepath):
    '''Read a JSON basis set file from a given path
    '''

    if not os.path.isfile(filepath):
        raise RuntimeError('Basis set file \'{}\' does not exist, is not '
                           'readable, or is not a file'.format(filepath))

    with open(filepath, 'r') as f:
        js = json.loads(f.read())

    # change the element keys to integers
    js['basisSetElements'] = {int(k): v for k, v in js['basisSetElements'].items()}

    return js


def write_json_basis_file(filepath, bs):
    '''Read a JSON basis set file to a given path
    '''
    with open(filepath, 'w') as f:
        json.dump(sort_basis_dict(bs), f, indent=4)


def read_json_basis(name):
    '''Reads a json basis set file given only the name

    The path to the basis set file is taken to be the 'basis' directory
    in this project
    '''

    bs_path = os.path.join(bs_data_path, name + '.json')

    if not os.path.isfile(bs_path):
        raise RuntimeError('Atom basis \'{}\' does not exist'.format(name))

    return read_json_basis_file(bs_path)


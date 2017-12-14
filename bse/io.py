'''
Functions for reading and writing the standard JSON-based
basis set format
'''

import json
import os
import glob
import collections


def sort_basis_dict(bs):
    '''Sorts a basis set dictionary into a standard order

    This allows the written file to be more easily read by humans by,
    for example, putting the name and description before more detailed fields
    '''

    keyorder = [
        'molssi_bse_magic',
        'basisSetName', 'basisSetDescription',
        'basisSetRole', 'basisSetElements', 'elementReferences', 'elementECPElectrons',
        'elementElectronShells', 'elementECP', 'elementComponents', 'elementEntry',
        'shellFunctionType', 'shellHarmonicType', 'shellRegion', 'shellAngularMomentum',
        'shellExponents', 'shellCoefficients', 'potentialECPType', 'potentialAngularMomentum',
        'potentialRExponents', 'potentialGaussianExponents', 'potentialCoefficients'
    ]

    # Add integers for the elements
    keyorder.extend(list(range(150)))

    bs_sorted = sorted(bs.items(), key=lambda x: keyorder.index(x[0]))
    bs_sorted = collections.OrderedDict(bs_sorted)

    for k, v in bs_sorted.items():
        if isinstance(v, dict):
            bs_sorted[k] = sort_basis_dict(v)
        elif k == 'elementElectronShells':
            bs_sorted[k] = [sort_basis_dict(x) for x in v]

    return bs_sorted


def read_json_basis(file_path):

    if not os.path.isfile(file_path):
        raise RuntimeError('Basis set file \'{}\' does not exist, is not '
                           'readable, or is not a file'.format(file_path))

    #print("Reading ", file_path)
    with open(file_path, 'r') as f:
        js = json.loads(f.read())

    # Check for magic key/number
    if not 'molssi_bse_magic' in js:
        raise RuntimeError('This file does not appear to be a BSE JSON file')

    # change the element keys to integers
    js['basisSetElements'] = {int(k): v for k, v in js['basisSetElements'].items()}

    return js


def read_schema(file_path):
    if not os.path.isfile(file_path):
        raise RuntimeError('Schema file \'{}\' does not exist, is not '
                           'readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.loads(f.read())

    return js


def dump_basis(bs):
    '''Returns a string with all the basis information (pretty-printed)
    '''
    return json.dumps(sort_basis_dict(bs), indent=4)


def write_json_basis(filepath, bs):
    '''Read a JSON basis set file to a given path

       The keys are first sorted into a standard order
    '''
    with open(filepath, 'w') as f:
        json.dump(sort_basis_dict(bs), f, indent=4)


def get_basis_filelist(data_dir):
    return glob.glob(os.path.join(data_dir, '*.table.json'))

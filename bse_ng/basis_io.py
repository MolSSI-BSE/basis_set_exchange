import json
import os
import copy
import collections

my_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(my_path)
bs_data_path = os.path.join(parent_path, 'basis')


def sort_basis_dict(bsdict):
    keyorder = ['basisSetName',
                'basisSetDescription',
                'basisSetRole',
                'basisSetRegion', 
                'basisSetComponents',
                'basisSetElements',

                'elementReference',
                'elementElectronShells',

                'shellFunctionType',
                'shellHarmonicType',
                'shellAngularMomentum',
                'shellExponents',
                'shellCoefficients'
                
                ]

    # Add integers for the elements
    keyorder.extend(list(range(150)))

    bs2 = sorted(bsdict.items(), key=lambda x: keyorder.index(x[0]))
    bs2 = collections.OrderedDict(bs2)

    for k,v in bs2.items():
        if isinstance(v, dict):
            bs2[k] = sort_basis_dict(v)
        elif k == 'elementElectronShells':
            bs2[k] = [ sort_basis_dict(x) for x in v ]

    return bs2


def read_json_basis_file(basis_file):
    if not os.path.isfile(basis_file):
        raise RuntimeError('Basis set file \'{}\' does not exist, is not '
                           'readable, or is not a file'.format(basis_file))

    with open(basis_file, 'r') as f:
        js = json.loads(f.read())

    # change the element keys to integers
    js['basisSetElements'] = {int(k): v for k, v in js['basisSetElements'].items()}

    return js


def write_json_basis_file(basis_file, bs):
    with open(basis_file, 'w') as f:
        json.dump(sort_basis_dict(bs), f, indent=4)


def read_json_basis(basis_name):
    bs_path = os.path.join(bs_data_path, basis_name + '.json')

    if not os.path.isfile(bs_path):
        raise RuntimeError('Atom basis \'{}\' does not exist'.format(basis_name))

    return read_json_basis_file(bs_path)


def read_full_basis(basis_name):
    bs_path = os.path.join(bs_data_path, basis_name + '.bas')

    if not os.path.isfile(bs_path):
        raise RuntimeError('Full basis \'{}\' does not exist'.format(basis_name))

    el_map = {}
    with open(bs_path, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            if l:
                s = l.split()
                el_map[int(s[0])] = s[1]

    return el_map

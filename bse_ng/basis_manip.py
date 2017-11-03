import json
import os
import copy
from bse_ng import basis_io


def merge_element_dict(parent, child):
    new_dict = copy.deepcopy(parent)
    for k,v in child.items():
        if not k in new_dict:
            new_dict[k] = v
        elif isinstance(v, list):
            new_dict[k].extend[v]
        elif isinstance(v, dict):
            new_dict[k] = merge_element_dict(new_dict[k], v)
        else:
            raise RuntimeError("Error merging type {}".format(type(v)))
    return new_dict


def uncontract_basis_general(basis):
    new_basis = copy.deepcopy(basis)

    for k,el in basis['elements'].items():
        for region_k,region in el['electronShells'].items():
            newshells = []
            for sh in region['shells']:
                if len(sh['coefficients']) == 1:
                    newshells.append(sh)
                elif len(sh['angularMomentum']) == 1:
                    for c in sh['coefficients']:
                        newsh = {k: v for k, v in sh.items() if k != 'coefficients'}
                        newsh['coefficients'] = [c]
                        newshells.append(newsh)
                else:
                    for i,c in enumerate(sh['coefficients']):
                        newsh = copy.deepcopy(sh)
                        newsh['angularMomentum'] = [sh['angularMomentum'][i]]
                        newsh['coefficients'] = [c]
                        newshells.append(newsh)

            
            new_basis['elements'][k]['electronShells'][region_k]['shells'] = newshells
    return new_basis


def uncontract_basis_segmented(basis):
    pass
            

def validate_basis(basis):
    #req_keys = ['name', 'version', 'elements']
    req_keys = []
    for k in req_keys:
        if k not in basis:
            raise RuntimeError('Missing key '.format(k))

    for el, v in basis['elements'].items():
        for sh in v['shells']:
            # if this is combined AM, then the number of general contractions
            # must equal the number of AM
            n_am = len(sh['angularMomentum'])
            n_gen = len(sh['coefficients'])
            n_prim = len(sh['exponents'])

            if n_am > 1 and n_gen != n_am:
                raise RuntimeError('Number of general contractions ({}) not '
                                   'compatible with AM={}'.format(n_gen, sh['angularMomentum']))

            for g in sh['coefficients']:
                if len(g) != n_prim:
                    raise RuntimeError('Inconsistent number of primitives for general contraction.\n'
                                       'Expected {}, got {}. Coefficients are: {} '.format(n_prim, len(g), g))


def get_atom_basis(basis_name):
    js = basis_io.read_json_basis(basis_name)

    # Do we need to load a parent basis?
    for el,data in js['elements'].items():
        if 'inherit' in data:
            newelement = copy.deepcopy(data)
            for p in data['inherit']:
                parent = get_atom_basis(p)
                parent_el = parent['elements'][el]
                newelement = merge_element_dict(parent_el, newelement)

            newelement.pop('inherit', None)
            js['elements'][el] = newelement

    return js


def broadcast_metadata(basis):
    new_basis = copy.deepcopy(basis)
    name = basis['name']
    harm = basis['harmonic']

    for k in basis['elements'].keys():
        new_basis['elements'][k]['name'] = name
        new_basis['elements'][k]['harmonic'] = harm

    return new_basis


def get_full_basis(basis_name):
    el_map = basis_io.read_full_basis(basis_name)

    full_basis = { "fullBasisName": basis_name,
                   "elements" : {} }
    for k,v in el_map.items():
        js = get_atom_basis(v)
        js = broadcast_metadata(js)
        full_basis['elements'][k] = js['elements'][k]

    return full_basis

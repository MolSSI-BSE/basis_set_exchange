from .g94 import *
from .nwchem import *
from .. import io

# dummy functions


def write_dict(bs):
    return bs


def write_json(bs):
    return io.dump_basis(bs)


converter_map = {'dict': write_dict, 'json': write_json, 'gaussian94': write_g94, 'nwchem': write_nwchem}

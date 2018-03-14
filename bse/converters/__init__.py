from .g94 import *
from .nwchem import *
from .. import io

# dummy functions
def write_json(bs):
    return io.dump_basis(bs)


converter_map = { 'json': { 'display': 'JSON',
                            'function': write_json },
                  'nwchem': { 'display': 'NWChem',
                              'function': write_nwchem },
                  'gaussian94': { 'display': 'Gaussian94',
                                  'function': write_g94 }
                }

'''
Conversion of basis sets to various formats
'''

from .g94 import *
from .nwchem import *
from .bsejson import *

converter_map = {
    'json': {
        'display': 'JSON',
        'function': write_json
    },
    'nwchem': {
        'display': 'NWChem',
        'function': write_nwchem
    },
    'gaussian94': {
        'display': 'Gaussian94',
        'function': write_g94
    }
}

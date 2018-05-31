'''
Conversion of basis sets to various formats
'''

from .g94 import *
from .nwchem import *
from .gamess_us import *
from .bsejson import *

converter_map = {
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'function': write_json,
    },
    'nwchem': {
        'display': 'NWChem',
        'extension': '.nw',
        'function': write_nwchem
    },
    'gaussian94': {
        'display': 'Gaussian94',
        'extension': '.gbs',
        'function': write_g94
    },
    'gamess_us': {
        'display': 'GAMESS US',
        'extension': '.bas',
        'function': write_gamess_us
    }
}

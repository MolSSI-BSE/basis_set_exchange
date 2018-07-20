'''
Conversion of basis sets to various formats
'''

from .bsejson import write_json
from .nwchem import write_nwchem
from .g94 import write_g94
from .gamess_us import write_gamess_us
from .psi4 import write_psi4

converter_map = {
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'comment': None,
        'function': write_json
    },
    'nwchem': {
        'display': 'NWChem',
        'extension': '.nw',
        'comment': '#',
        'function': write_nwchem
    },
    'gaussian94': {
        'display': 'Gaussian94',
        'extension': '.gbs',
        'comment': '!',
        'function': write_g94
    },
    'gamess_us': {
        'display': 'GAMESS US',
        'extension': '.bas',
        'comment': '!',
        'function': write_gamess_us
    },
    'psi4': {
        'display': 'Psi4',
        'extension': '.gbs',
        'comment': '!',
        'function': write_psi4
    }
}

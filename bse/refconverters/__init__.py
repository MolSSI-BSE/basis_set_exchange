'''
Conversion of references to various formats
'''

from .bib import *
from .txt import *
from .bsejson import *

converter_map = {
    'json': {
        'display': 'JSON',
        'function': write_json
    },
    'bib': {
        'display': 'BibTeX',
        'function': write_bib
    },
    'txt': {
        'display': 'Plain Text',
        'function': write_txt
    }
}

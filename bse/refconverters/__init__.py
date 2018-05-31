'''
Conversion of references to various formats
'''

from .bib import *
from .txt import *
from .bsejson import *

converter_map = {
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'function': write_json
    },
    'bib': {
        'display': 'BibTeX',
        'extension': '.bib',
        'function': write_bib
    },
    'txt': {
        'display': 'Plain Text',
        'extension': '.txt',
        'function': write_txt
    }
}

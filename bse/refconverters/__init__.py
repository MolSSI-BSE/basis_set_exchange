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
        'comment': None,
        'function': write_json
    },
    'bib': {
        'display': 'BibTeX',
        'extension': '.bib',
        'comment': '%',
        'function': write_bib
    },
    'txt': {
        'display': 'Plain Text',
        'extension': '.txt',
        'comment': None,
        'function': write_txt
    }
}

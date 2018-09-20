'''
Conversion of references to various formats
'''

from .bib import write_bib
from .txt import write_txt
from .bsejson import write_json

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

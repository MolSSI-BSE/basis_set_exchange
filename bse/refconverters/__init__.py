import json
from .bib import *
from .txt import *

# dummy functions

def write_json(refs):
    return json.dumps(refs)


converter_map = { 'json' : { 'display': 'JSON', 
                             'function': write_json },
                  'bib': { 'display': 'BibTeX',
                           'function': write_bib },
                  'txt': { 'display': 'Plain Text',
                           'function': write_txt }
                 }


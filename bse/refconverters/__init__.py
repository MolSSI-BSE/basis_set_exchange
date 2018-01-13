from .bib import *
from .txt import *

# dummy functions

def write_dict(refs):
    return refs

def write_json(refs):
    return json.dumps(refs)

converter_map = { 'dict': write_dict,
                  'json': write_json,
                  'bib': write_bib,
                  'txt': write_txt
                 }


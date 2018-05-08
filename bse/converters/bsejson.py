'''
Conversion of basis sets to JSON format
'''

import json


def write_json(bs):
    '''Converts a basis set to JSON
    '''
    return json.dumps(bs, indent=4, ensure_ascii=False)

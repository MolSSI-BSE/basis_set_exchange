'''
Conversion of basis sets to JSON format
'''

import json


def write_json(basis):
    '''Converts a basis set to JSON
    '''

    return json.dumps(basis, indent=4, ensure_ascii=False)

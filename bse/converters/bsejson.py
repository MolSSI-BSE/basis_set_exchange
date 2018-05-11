'''
Conversion of basis sets to JSON format
'''

import json


def write_json(header, basis):
    '''Converts a basis set to JSON
    '''

    # Ignore the header
    return json.dumps(basis, indent=4, ensure_ascii=False)

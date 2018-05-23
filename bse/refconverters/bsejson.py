'''
Conversion of references to JSON format
'''

import json


def write_json(refs):
    '''Converts references to JSON format
    '''

    return json.dumps(refs, indent=4, ensure_ascii=False)

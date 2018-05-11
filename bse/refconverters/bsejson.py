'''
Conversion of references to JSON format
'''

import json


def write_json(header, refs):
    '''Converts references to JSON format
    '''

    # Ignore the header
    return json.dumps(refs, indent=4, ensure_ascii=False)

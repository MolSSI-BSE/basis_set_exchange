'''
Functionality for handling basis set and family notes
'''

import os
import textwrap
from . import fileio
from . import references


def process_notes(notes, data_dir):
    '''Add reference information to the bottom of a notes file

    `:ref:` tags are removed and the actual reference data is appended
    '''

    reffile_path = os.path.join(data_dir, 'REFERENCES.json')
    ref_data = fileio.read_references(reffile_path)            

    ref_keys = ref_data.keys()

    found_refs = set()
    for k in ref_keys:
        if k in notes:
            found_refs.add(k)

    # The block to append
    reference_sec = '\n\n'
    reference_sec += '-------------------------------------\n'
    reference_sec += ' REFERENCES\n'
    reference_sec += '-------------------------------------\n'

    # Add reference data
    for r in sorted(found_refs):
        rtxt= references.reference_text(ref_data[r])
        reference_sec += r + '\n'
        reference_sec += textwrap.indent(rtxt, ' '*4)
        reference_sec += '\n\n'

    return notes + reference_sec

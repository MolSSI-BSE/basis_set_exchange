"""
Functionality for handling basis set and family notes
"""

from . import references


def process_notes(notes, ref_data):
    """Add reference information to the bottom of a notes file

    `:ref:` tags are removed and the actual reference data is appended
    """

    ref_keys = ref_data.keys()

    found_refs = set()
    for k in ref_keys:
        if k in notes:
            found_refs.add(k)

    # The block to append
    reference_sec = "\n\n"
    reference_sec += "-------------------------------------------------\n"
    reference_sec += " REFERENCES MENTIONED ABOVE\n"
    reference_sec += " (not necessarily references for the basis sets)\n"
    reference_sec += "-------------------------------------------------\n"

    # Add reference data
    if not found_refs:
        return notes

    for r in sorted(found_refs):
        rtxt = references.reference_text(r, ref_data[r])
        reference_sec += rtxt + "\n\n"

    return notes + reference_sec

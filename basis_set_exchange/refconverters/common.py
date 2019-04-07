'''
Helper functions for writing out basis set references in various formats
'''

from .. import api

_lib_refs = ["pritchardXXXXa", "feller1996a", "schuchardt2007a"]
_lib_refs_desc = 'If you downloaded data from the basis set\nexchange or used the basis set exchange python library, please cite:\n'


def get_library_citation():
    '''Return a descriptive string and reference data for what users of the library should cite'''

    all_ref_data = api.get_reference_data()
    lib_refs_data = {k: all_ref_data[k] for k in _lib_refs}
    return (_lib_refs_desc, lib_refs_data)

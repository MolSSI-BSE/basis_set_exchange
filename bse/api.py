'''
Main interface to BSE functionality
'''

from bse import io

def get_basis_set(name):

    '''Reads a json basis set file given only the name

    The path to the basis set file is taken to be the 'data' directory
    in this project
    '''

    return io.read_table_basis_by_name(name)


def get_metadata(keys=None, key_filter=None):
    if key_filter:
        raise RuntimeError("key_filter not implemented")

    avail_names = io.get_available_names()

    metadata = {}
    for n in avail_names:
        bs = io.read_table_basis_by_name(n)
        common_name = bs['basisSetName']
        defined_elements = list(bs['basisSetElements'].keys())

        function_types = set()
        for e in bs['basisSetElements'].values():
            for s in e['elementElectronShells']:
                function_types.add(s['shellFunctionType'])

        metadata[common_name] = {
            'filename': n,
            'elements': defined_elements, 
            'functiontypes': list(function_types),
        }

    return metadata

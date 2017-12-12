'''
Main interface to BSE functionality
'''

from . import io
from . import manip
from . import converters


def get_basis_set(name,
                  elements=None,
                  fmt='dict',
                  uncontract_general=False,
                  uncontract_spdf=False,
                  uncontract_segmented=False):
    '''Reads a json basis set file given only the name

    The path to the basis set file is taken to be the 'data' directory
    in this project
    '''

    bs = io.read_table_basis_by_name(name)

    # Handle optional arguments
    if elements is not None:
        bs_elements = bs['basisSetElements']

        # Are elements part of this basis set?
        for el in elements:
            if not el in bs_elements:
                raise RuntimeError("Element {} not found in basis {}".format(el, name))

            bs['basisSetElements'] = { k:v for k, v in bs_elements.items() if k in elements }

    if uncontract_general:
        bs = manip.uncontract_general(bs)
    if uncontract_spdf:
        bs = manip.uncontract_spdf(bs)
    if uncontract_segmented:
        bs = manip.uncontract_segmented(bs)

    if not fmt in converters.converter_map:
        raise RuntimeError('Unknown format {}'.format(fmt))
    else:
        return converters.converter_map[fmt](bs)

    return bs


def get_metadata(keys=None, key_filter=None):
    if key_filter:
        raise RuntimeError("key_filter not implemented")

    avail_names = io.get_available_names()

    metadata = {}
    for n in avail_names:
        bs = io.read_table_basis_by_name(n)
        displayname = bs['basisSetName']
        defined_elements = list(bs['basisSetElements'].keys())

        function_types = set()
        for e in bs['basisSetElements'].values():
            for s in e['elementElectronShells']:
                function_types.add(s['shellFunctionType'])

        metadata[n] = {
            'displayname': displayname,
            'elements': defined_elements,
            'functiontypes': list(function_types),
        }

    return metadata


def get_formats():
    return list(converters.converter_map.keys())

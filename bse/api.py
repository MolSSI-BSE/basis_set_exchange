'''
Main interface to BSE functionality
'''

import os
import json
from . import io
from . import manip
from . import compose
from . import references
from . import converters
from . import refconverters

# Determine the path to the data directory
my_dir = os.path.dirname(os.path.abspath(__file__))
default_data_dir = os.path.join(my_dir, 'data')
default_schema_dir = os.path.join(my_dir, 'schema')


def get_basis_set(name,
                  data_dir=default_data_dir,
                  elements=None,
                  fmt='dict',
                  uncontract_general=False,
                  uncontract_spdf=False,
                  uncontract_segmented=False):
    '''Reads a json basis set file given only the name

    The path to the basis set file is taken to be the 'data' directory
    in this project
    '''

    table_basis_path = os.path.join(data_dir, name + '.table.json')
    bs = compose.compose_table_basis(table_basis_path)

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


def get_metadata(keys=None, key_filter=None, data_dir=default_data_dir):
    if key_filter:
        raise RuntimeError("key_filter not implemented")

    basis_filelist = io.get_basis_filelist(data_dir)

    metadata = {}
    for n in basis_filelist:
        bs = compose.compose_table_basis(n)
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


def get_references(name,
                   data_dir=default_data_dir,
                   reffile_name='REFERENCES.json',
                   elements=None,
                   fmt='dict'):

    reffile_path = os.path.join(data_dir, reffile_name)

    basis_dict = get_basis_set(name, 
                               data_dir=data_dir,
                               elements=elements,
                               fmt='dict')

    ref_data = references.compact_references(basis_dict, reffile_path)

    if not fmt in refconverters.converter_map:
        raise RuntimeError('Unknown format {}'.format(fmt))
    else:
        return refconverters.converter_map[fmt](ref_data)

    return ref_data 


def get_schema(schema_type):
    schema_file = "{}-schema.json".format(schema_type)
    file_path = os.path.join(default_schema_dir, schema_file)

    if not os.path.isfile(file_path):
        raise RuntimeError('Schema file \'{}\' does not exist, is not '
                           'readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.load(f)

    return js



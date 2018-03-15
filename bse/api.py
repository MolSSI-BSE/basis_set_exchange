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

# Determine the path to the data directory that is part
# of this installation
my_dir = os.path.dirname(os.path.abspath(__file__))
default_data_dir = os.path.join(my_dir, 'data')
default_schema_dir = os.path.join(my_dir, 'schema')


def get_basis_set(name,
                  data_dir=default_data_dir,
                  elements=None,
                  version=None,
                  fmt=None,
                  uncontract_general=False,
                  uncontract_spdf=False,
                  uncontract_segmented=False):
    '''Reads a json basis set file given only the name

    The path to the basis set file is taken to be the 'data' directory
    in this project

    fmt is case insensitive
    '''

    metadata = get_metadata(data_dir)

    if not name in metadata:
        raise RuntimeError("Basis set {} does not exist".format(name))

    bs_data = metadata[name]

    if version is None:
        version = bs_data['latest_version']

    table_basis_path = os.path.join(data_dir, bs_data['versions'][version]['filename'])
    bs = compose.compose_table_basis(table_basis_path)

    # Handle optional arguments
    if elements is not None:
        bs_elements = bs['basisSetElements']

        # Are elements part of this basis set?
        for el in elements:
            if not el in bs_elements:
                raise RuntimeError("Element {} not found in basis {}".format(el, name))

            bs['basisSetElements'] = {k: v for k, v in bs_elements.items() if k in elements}

    if uncontract_general:
        bs = manip.uncontract_general(bs)
    if uncontract_spdf:
        bs = manip.uncontract_spdf(bs)
    if uncontract_segmented:
        bs = manip.uncontract_segmented(bs)

    if fmt is None:
        return bs

    # make converters case insensitive
    fmt = fmt.lower()
    if fmt in converters.converter_map:
        return converters.converter_map[fmt]['function'](bs)
    else:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))


def get_metadata(data_dir=default_data_dir):
    metadata_file = os.path.join(data_dir, "METADATA.json")
    return io.read_metadata(metadata_file)


def get_formats():
    return { k:v['display'] for k,v in converters.converter_map.items() }


def get_references(name, version=None, data_dir=default_data_dir, reffile_name='REFERENCES.json', elements=None, fmt=None):

    reffile_path = os.path.join(data_dir, reffile_name)

    basis_dict = get_basis_set(name, version=version, data_dir=data_dir, elements=elements, fmt=None)

    ref_data = references.compact_references(basis_dict, reffile_path)

    if fmt is None:
        return ref_data

    # Make fmt case insensitive
    fmt = fmt.lower()
    if fmt in refconverters.converter_map:
        return refconverters.converter_map[fmt]['function'](ref_data)
    else:
        raise RuntimeError('Unknown reference format "{}"'.format(fmt))

    return ref_data


def get_reference_formats():
    return { k:v['display'] for k,v in refconverters.converter_map.items() }


def get_schema(schema_type):
    schema_file = "{}-schema.json".format(schema_type)
    file_path = os.path.join(default_schema_dir, schema_file)

    if not os.path.isfile(file_path):
        raise RuntimeError('Schema file \'{}\' does not exist, is not readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.load(f)

    return js

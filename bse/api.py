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

    if version is None:
        version = io.get_latest_version_number(name, data_dir)

    table_basis_path = io.get_basis_file_path(name, version, data_dir)

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


def get_metadata(keys=None, key_filter=None, data_dir=default_data_dir):
    if key_filter:
        raise NotImplementedError("key_filter not implemented")

    basis_filelist = io.get_basis_filelist(data_dir)

    metadata = {}
    for bs_file_path in basis_filelist:
        # Actually compose the basis set from components
        bs = compose.compose_table_basis(bs_file_path)

        # Prepare the metadata
        displayname = bs['basisSetName']
        defined_elements = list(bs['basisSetElements'].keys())
        revision_desc = bs['basisSetRevisionDescription']

        function_types = set()
        for e in bs['basisSetElements'].values():
            for s in e['elementElectronShells']:
                function_types.add(s['shellFunctionType'])
            if 'elementECP' in e:
                function_types.add('ECP')

        # convert the file path to the internal identifier for the basis set
        internal_name = os.path.basename(bs_file_path)
        internal_name = internal_name.replace(".table.json", "")

        # split out the version number
        internal_name,ver = os.path.splitext(internal_name)
        ver = int(ver[1:])

        single_meta = { 
            'revdesc': revision_desc,
            'elements': defined_elements,
            'functiontypes': list(function_types),
        }

        # Select specific keys if key_filter is given
        if keys is not None:
            all_keys = list(single_meta.keys())
            for k in all_keys:
                if not k in keys:
                    single_meta.pop(k)

        if not displayname in metadata: 
            metadata[displayname] = {ver: single_meta}
        else:
            metadata[displayname][ver] = single_meta

    return metadata


def get_formats():
    return converters.converter_map.keys()


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
    return refconverters.converter_map.keys()


def get_schema(schema_type):
    schema_file = "{}-schema.json".format(schema_type)
    file_path = os.path.join(default_schema_dir, schema_file)

    if not os.path.isfile(file_path):
        raise RuntimeError('Schema file \'{}\' does not exist, is not readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.load(f)

    return js

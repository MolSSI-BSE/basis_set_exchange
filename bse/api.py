'''
Main interface to Basis Set Exchange functionality
'''

import os
import json
from . import fileio
from . import lut
from . import manip
from . import compose
from . import references
from . import converters
from . import refconverters

# Determine the path to the data directory that is part
# of this installation
_my_dir = os.path.dirname(os.path.abspath(__file__))
_default_data_dir = os.path.join(_my_dir, 'data')
_default_schema_dir = os.path.join(_my_dir, 'schema')


def _convert_element_list(elements):
    '''Convert a list of elements to an internal list

    A list of elements can contain both integers and strings.
    This converts the list entirely to integers
    '''

    ret = []
    for el in elements:
        if isinstance(el, str):
            ret.append(lut.element_Z_from_sym(el))
        else:
            ret.append(el)

    return ret


def get_basis(name,
              elements=None,
              version=None,
              fmt=None,
              optimize_general=False,
              uncontract_general=False,
              uncontract_spdf=False,
              uncontract_segmented=False,
              data_dir=None):
    '''Obtain a basis set

    This is the main function for getting basis set information.
    This function reads in all the basis data and returns it either
    as a string or as a python dictionary.

    Parameters
    ----------
    name : str
        Name of the basis set. This is not case sensitive.
    elements : list
        List of elements that you want the basis set for. By default,
        all elements for which the basis set is defined are included.
        Elements can be specified by Z-number (int) or by symbol (string)
    version : int
        Obtain a specific version of this basis set. By default,
        the latest version is returned.
    fmt: str
        What format to return the basis set as. By defaut,
        basis set information is returned as a python dictionary. Otherwise,
        if a format is specified, a string is returned.
        Use :func:`bse.api.get_formats` to obtain the available formats.
    optimize_general : bool
        Optimize by removing general contractions that contain uncontracted
        functions (see :func:`bse.manip.optimize_general`)
    uncontract_general : bool
        If True, remove general contractions by duplicating the set
        of primitive exponents with each vector of coefficients.
        Primitives with zero coefficient are removed, as are duplicate shells.
    uncontract_spdf : bool
        If True, remove general contractions with combined angular momentum (sp, spd, etc)
        by duplicating the set of primitive exponents with each vector of coefficients.
        Primitives with zero coefficient are removed, as are duplicate shells.
    uncontract_segmented : bool
        If True, remove segmented contractions by duplicating each primitive into new shells.
        Each coefficient is set to 1.0
    data_dir : str
        Data directory with all the basis set information. By default,
        it is in the 'data' subdirectory of this project.
    '''

    if data_dir is None:
        data_dir = _default_data_dir

    # Transform the name into an internal representation
    tr_name = manip.transform_basis_name(name)

    # Get the metadata for all basis sets
    metadata = get_metadata(data_dir)

    if not tr_name in metadata:
        raise KeyError("Basis set {} does not exist".format(name))

    bs_data = metadata[tr_name]

    # If version is not specified, use the latest
    if version is None:
        version = bs_data['latest_version']

    # Compose the entire basis set (all elements)
    table_basis_path = os.path.join(data_dir, bs_data['versions'][version]['filename'])
    basis_dict = compose.compose_table_basis(table_basis_path)

    # Handle optional arguments
    if elements is not None:
        # Convert to purely a list of integers
        elements = _convert_element_list(elements)

        bs_elements = basis_dict['basis_set_elements']

        # Are elements part of this basis set?
        for el in elements:
            if not el in bs_elements:
                raise KeyError("Element {} not found in basis {}".format(el, name))

            # Set to only the elements we want
            basis_dict['basis_set_elements'] = {k: v for k, v in bs_elements.items() if k in elements}

    if optimize_general:
        basis_dict = manip.optimize_general(basis_dict)
    if uncontract_general:
        basis_dict = manip.uncontract_general(basis_dict)
    if uncontract_spdf:
        basis_dict = manip.uncontract_spdf(basis_dict)
    if uncontract_segmented:
        basis_dict = manip.uncontract_segmented(basis_dict)

    # If fmt is not specified, return as a python dict
    if fmt is None:
        return basis_dict

    # What should we put at the top?
    header = u'Basis Set Exchange: {} ({})'.format(name, basis_dict['basis_set_description'])

    # make converters case insensitive
    fmt = fmt.lower()
    if fmt in converters.converter_map:
        return converters.converter_map[fmt]['function'](header, basis_dict)
    else:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))


def get_metadata(data_dir=None):
    '''Obtain the metadata for all basis sets

    The metadata includes information such as the display name of the basis set,
    its versions, and what elements are included in the basis set

    The data is read from the METADATA.json file in the `data_dir` directory.

    Parameters
    ----------
    data_dir : str
        Data directory with all the basis set information. By default,
        it is in the 'data' subdirectory of this project.
    '''

    if data_dir is None:
        data_dir = _default_data_dir

    metadata_file = os.path.join(data_dir, "METADATA.json")
    return fileio.read_metadata(metadata_file)


def get_all_basis_names(data_dir=None):
    '''Obtain a list of all basis set names

    The returned list is the internal representation of the basis set name.

    The data is read from the METADATA.json file in the data directory.

    Parameters
    ----------
    data_dir : str
        Data directory with all the basis set information. By default,
        it is in the 'data' subdirectory of this project.
    '''

    return sorted(list(get_metadata(data_dir).keys()))


def get_references(name, elements=None, version=None, fmt=None, data_dir=None):
    '''Get the references/citations for a basis set

    The reference data is read from the REFERENCES.json file in the given
    `data_dir` directory.

    Parameters
    ----------
    name : str
        Name of the basis set. This is not case sensitive.
    elements : list
        List of element numbers that you want the basis set for. By default,
        all elements for which the basis set is defined are included.
    version : int
        Obtain a specific version of this basis set. By default,
        the latest version is returned.
    fmt: str
        What format to return the basis set as. By defaut,
        basis set information is returned as a list of dictionaries. Use
        get_reference_formats() to obtain the available formats.
    data_dir : str
        Data directory with all the basis set information. By default,
        it is in the 'data' subdirectory of this project.
    '''

    if data_dir is None:
        data_dir = _default_data_dir

    reffile_path = os.path.join(data_dir, 'REFERENCES.json')

    basis_dict = get_basis(name, version=version, data_dir=data_dir, elements=elements, fmt=None)

    ref_data = references.compact_references(basis_dict, reffile_path)

    if fmt is None:
        return ref_data

    # What should we put at the top?
    header = u'Basis Set Exchange: {} ({})'.format(name, basis_dict['basis_set_description'])

    # Make fmt case insensitive
    fmt = fmt.lower()
    if fmt in refconverters.converter_map:
        return refconverters.converter_map[fmt]['function'](header, ref_data)
    else:
        raise RuntimeError('Unknown reference format "{}"'.format(fmt))

    return ref_data


def get_schema(schema_type):
    '''Get a schema that can validate BSE JSON files

       The schema_type represents the type of BSE JSON file to be validated,
       and can be 'component', 'element', 'table', or 'references'.
    '''

    schema_file = "{}-schema.json".format(schema_type)
    file_path = os.path.join(_default_schema_dir, schema_file)

    if not os.path.isfile(file_path):
        raise RuntimeError('Schema file \'{}\' does not exist, is not readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.load(f)

    return js


def get_formats():
    '''Return information about the basis set formats available

    The returned data is a map of format to display name. The format
    can be passed as the fmt argument to :func:`get_basis()`
    '''
    return {k: v['display'] for k, v in converters.converter_map.items()}


def get_reference_formats():
    '''Return information about the reference/citation formats available

    The returned data is a map of format to display name. The format
    can be passed as the fmt argument to :func:`get_references`
    '''
    return {k: v['display'] for k, v in refconverters.converter_map.items()}

"""
Functions for reading and writing the standard JSON-based
basis set format
"""

import codecs
import collections
import json
import os


def _read_plain_json(file_path, check_bse):
    """
    Reads a JSON file

    A simple wrapper around json.load that only takes the file name
    If the file does not exist, an exception is thrown.

    If the file does exist, but there is a problem with the JSON formatting,
    the filename is added to the exception information.

    If check_bse is True, this function also make sure the 'molssi_bse_schema' key
    exists in the file.

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError('JSON file \'{}\' does not exist, is not '
                                'readable, or is not a file'.format(file_path))

    try:
        with open(file_path, 'r') as f:
            js = json.load(f)
    except json.decoder.JSONDecodeError as ex:
        raise RuntimeError("File {} contains JSON errors".format(file_path)) from ex

    if check_bse is True:
        # Check for molssi_bse_schema key
        if 'molssi_bse_schema' not in js:
            raise RuntimeError('File {} does not appear to be a BSE JSON file'.format(file_path))

    return js


def _write_plain_json(file_path, js):
    """
    Write information to a JSON file

    This makes sure files are created with the proper encoding and consistent indenting

    Parameters
    ----------
    file_path : str
        Full path to the file to write to. It will be overwritten if it exists
    js : dict
        JSON information to write
    """

    # Disable ascii in the json - this prevents the json writer
    # from escaping everything
    with codecs.open(file_path, 'w', 'utf-8') as f:
        json.dump(js, f, indent=4, ensure_ascii=False)


def _sort_basis_dict(bs):
    """Sorts a basis set dictionary into a standard order

    This allows the written file to be more easily read by humans by,
    for example, putting the name and description before more detailed fields.
    This is purely for cosmetic reasons.
    """

    _keyorder = [
        'molssi_bse_schema', 'schema_type', 'schema_version', 'basis_set_name', 'basis_set_family',
        'basis_set_description', 'basis_set_revision_description', 'basis_set_role', 'basis_set_auxiliaries',
        'basis_set_references', 'basis_set_notes', 'basis_set_elements', 'element_references', 'element_ecp_electrons',
        'element_electron_shells', 'element_ecp', 'element_components', 'element_entry', 'shell_function_type',
        'shell_harmonic_type', 'shell_region', 'shell_angular_momentum', 'shell_exponents', 'shell_coefficients',
        'potential_ecp_type', 'potential_angular_momentum', 'potential_r_exponents', 'potential_gaussian_exponents',
        'potential_coefficients', 'rifit'
    ]

    # Add integers for the elements (being optimistic that element 150 will be found someday)
    _keyorder.extend([str(x) for x in range(150)])

    bs_sorted = sorted(bs.items(), key=lambda x: _keyorder.index(x[0]))
    bs_sorted = collections.OrderedDict(bs_sorted)

    for k, v in bs_sorted.items():
        # If this is a dictionary, sort recursively
        # If this is a list, sort each element but DO NOT sort the list itself.
        if isinstance(v, dict):
            bs_sorted[k] = _sort_basis_dict(v)
        elif isinstance(v, list):
            # Note - the only nested list is with coeffs, which shouldn't be sorted
            #        (so we don't have to recurse into lists of lists)
            bs_sorted[k] = [_sort_basis_dict(x) if isinstance(x, dict) else x for x in v]

    return bs_sorted


def _sort_references_dict(refs):
    """Sorts a references dictionary into a standard order

    The keys of the references are also sorted, and the keys for the data for each
    reference are put in a more canonical order.

    This allows the written file to be more easily read by humans by,
    for example, putting the the title and authos first, followed by more detailed information.
    This is purely for cosmetic reasons.
    """

    _keyorder = [
        'schema_type', 'schema_version', 'type', 'authors', 'title', 'booktitle', 'series', 'editors', 'journal',
        'institution', 'volume', 'number', 'page', 'year', 'note', 'publisher', 'address', 'isbn', 'doi'
    ]

    refs_sorted = collections.OrderedDict()

    refs_sorted['molssi_bse_schema'] = refs['molssi_bse_schema']
    for k in sorted(refs.keys()):
        sorted_entry = sorted(refs[k].items(), key=lambda x: _keyorder.index(x[0]))
        refs_sorted[k] = collections.OrderedDict(sorted_entry)

    return refs_sorted


def read_json_basis(file_path):
    """
    Reads generic basis set information from a JSON file

    After reading, the MolSSI BSE schema information is searched for and if not
    found, an exception is raised.

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    return _read_plain_json(file_path, True)


def read_schema(file_path):
    """
    Reads a JSON schema file

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    return _read_plain_json(file_path, False)


def read_references(file_path):
    """
    Reads a references JSON file

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    return _read_plain_json(file_path, True)


def read_metadata(file_path):
    """
    Reads a file containing the metadata for all the basis sets

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    return _read_plain_json(file_path, False)


def write_json_basis(file_path, bs):
    """
    Write basis set information to a JSON file

    Parameters
    ----------
    file_path : str
        Full path to the file to write to. It will be overwritten if it exists
    bs : dict
        Basis set information to write
    """

    _write_plain_json(file_path, _sort_basis_dict(bs))


def write_references(file_path, refs):
    """
    Write reference information to a JSON file

    Parameters
    ----------
    file_path : str
        Full path to the file to write to. It will be overwritten if it exists
    refs : dict
        Reference information to write
    """

    _write_plain_json(file_path, _sort_references_dict(refs))


def get_basis_filelist(data_dir):
    """
    Returns the relative paths to all the table basis sets contained
    in the given data directory
    """

    return get_all_filelist(data_dir)[0]


def get_all_filelist(data_dir):
    """
    Returns a tuple containing the following (as lists)

    1. All table basis files
    2. All element basis files
    3. All component basis files

    The paths to all the files are returned as paths relative to data_dir
    """

    all_table = []
    all_element = []
    all_component = []

    special = ['METADATA.json', 'REFERENCES.json']

    for root, dirs, files in os.walk(data_dir):
        for basename in files:
            if basename in special:
                continue

            fpath = os.path.join(root, basename)
            fpath = os.path.relpath(fpath, data_dir)

            if basename.endswith('.table.json'):
                all_table.append(fpath)
            elif basename.endswith('.element.json'):
                all_element.append(fpath)
            elif basename.endswith('.json'):
                all_component.append(fpath)

    return (all_table, all_element, all_component)


def read_notes_file(file_path):
    """
    Returns the contents of a notes file.

    If the notes file does not exist, None is returned
    """

    if not os.path.isfile(file_path):
        return None

    with open(file_path, 'r') as f:
        return f.read()

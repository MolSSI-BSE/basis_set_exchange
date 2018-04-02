"""
Functions for reading and writing the standard JSON-based
basis set format
"""

import json
import os
import glob
import collections
import codecs


def _sort_basis_dict(bs):
    """Sorts a basis set dictionary into a standard order

    This allows the written file to be more easily read by humans by,
    for example, putting the name and description before more detailed fields.
    This is purely for cosmetic reasons.
    """

    keyorder = [
        'molssi_bse_schema', 'schema_type', 'schema_version', 'basis_set_name', 'basis_set_description', 'basis_set_revision_description', 'basis_set_role',
        'basis_set_references', 'basis_set_notes', 'basis_set_elements', 'element_references',
        'element_ecp_electrons', 'element_electron_shells', 'element_ecp', 'element_components', 'element_entry',
        'shell_function_type', 'shell_harmonic_type', 'shell_region', 'shell_angular_momentum', 'shell_exponents',
        'shell_coefficients', 'potential_ecp_type', 'potential_angular_momentum', 'potential_r_exponents',
        'potential_gaussian_exponents', 'potential_coefficients'
    ]

    # Add integers for the elements
    keyorder.extend(list(range(150)))

    bs_sorted = sorted(bs.items(), key=lambda x: keyorder.index(x[0]))
    bs_sorted = collections.OrderedDict(bs_sorted)

    for k, v in bs_sorted.items():
        if isinstance(v, dict):
            bs_sorted[k] = _sort_basis_dict(v)
        elif k == 'element_electron_shells':
            bs_sorted[k] = [_sort_basis_dict(x) for x in v]

    return bs_sorted


def _sort_references_dict(refs):
    """Sorts a references dictionary into a standard order

    This sorts by key
    """

    refs_sorted = sorted(refs.items())
    refs_sorted = collections.OrderedDict(refs_sorted)
    return refs_sorted


def read_json_basis(file_path):
    """
    Reads generic basis set information from a JSON file

    After reading, the MolSSI BSE magic key is searched for and if not
    found, an exception is raised.

    The keys for the elements within a basis set (the Z number) is converted
    to integers (from strings) in this function.

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    if not os.path.isfile(file_path):
        raise RuntimeError('Basis set file \'{}\' does not exist, is not '
                           'readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.load(f)

    # Check for molssi_bse_schema key
    if 'molssi_bse_schema' not in js:
        raise RuntimeError('This file does not appear to be a BSE JSON file')

    # change the element keys to integers
    js['basis_set_elements'] = {int(k): v for k, v in js['basis_set_elements'].items()}

    return js


def read_schema(file_path):
    """
    Reads a JSON schema file

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    if not os.path.isfile(file_path):
        raise RuntimeError('Schema file \'{}\' does not exist, is not ' 'readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.load(f)

    return js


def read_references(file_path):
    """
    Reads a references JSON file

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    if not os.path.isfile(file_path):
        raise RuntimeError('References file \'{}\' does not exist, is not '
                           'readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.load(f)

    return js


def read_metadata(file_path):
    """
    Reads a file containing the metadata for all the basis sets

    Parameters
    ----------
    file_path : str
        Full path to the file to read
    """

    if not os.path.isfile(file_path):
        raise RuntimeError('Metadata file \'{}\' does not exist, is not '
                           'readable, or is not a file'.format(file_path))

    with open(file_path, 'r') as f:
        js = json.load(f)

    # Change version numbers to integers
    for k,v in js.items():
        v['versions'] = { int(k2):v2 for k2,v2 in v['versions'].items() }

    return js


def dump_basis(bs):
    """
    Returns a string with all the basis information (pretty-printed)
    """

    return json.dumps(_sort_basis_dict(bs), indent=4)


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

    # Disable ascii in the json - this prevents the json writer
    # from escaping everything
    with codecs.open(file_path, 'w', 'utf-8') as f:
        json.dump(_sort_basis_dict(bs), f, indent=4, ensure_ascii=False)


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

    # Disable ascii in the json - this prevents the json writer
    # from escaping everything
    with codecs.open(file_path, 'w', 'utf-8') as f:
        json.dump(_sort_references_dict(refs), f, indent=4, ensure_ascii=False)


def get_basis_filelist(data_dir):
    """
    Returns the full paths to all the full, table basis sets contained
    in the given data directory
    """

    return glob.glob(os.path.join(data_dir, '*.table.json'))


def get_files_for_basis(basis_name, data_dir):
    """
    Searches the filesystem for a basis with the given 'display' name and
    returns which files contain that basis
    """

    all_basis_files = get_basis_filelist(data_dir)

    containing_files = []

    for basis_file in all_basis_files:
        displayname = read_json_basis(basis_file)['basis_set_name']
        if displayname == basis_name:
            containing_files.append(basis_file)

    return containing_files


def get_basis_file_path(basis_name, version, data_dir):

    basis_files = get_files_for_basis(basis_name, data_dir)

    if len(basis_files) == 0:
        raise RuntimeError('Basis set \'{}\' does not exist'.format(basis_name, version))

    for bf in basis_files:
        if bf.endswith('{}.table.json'.format(version)):
            return bf 
    else:
        raise RuntimeError('Basis set \'{}\' (version {}) does not exist, or the '
                           'basis set file is not readable'.format(basis_name, version))
    

def get_latest_version_number(basis_name, data_dir):
    """
    Searches the filesystem for a basis with the given internal name and
    returns an integer representing the latest version
    """

    all_version_files = get_files_for_basis(basis_name, data_dir)

    if len(all_version_files) == 0:
        raise RuntimeError('Basis set \'{}\' does not exist'.format(basis_name))

    all_versions = [ int(x.split('.')[-3]) for x in all_version_files ]
    return sorted(all_versions)[-1]

# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Functions for reading and writing the standard JSON-based
basis set format
"""

import json
import bz2
import os

from .sort import sort_basis_dict, sort_references_dict

# The encoding to use for reading/writing files.
# For all the files in the project, UTF-8 is used
_default_encoding = 'utf-8'


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
    check_bse: bool
        If True, check to make sure the bse schema information is included.
        If not found, an exception is raised
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError('JSON file \'{}\' does not exist, is not '
                                'readable, or is not a file'.format(file_path))

    try:
        if file_path.endswith('.bz2'):
            with bz2.open(file_path, 'rt', encoding=_default_encoding) as f:
                js = json.load(f)
        else:
            with open(file_path, 'r', encoding=_default_encoding) as f:
                js = json.load(f)

    except json.decoder.JSONDecodeError as ex:
        raise RuntimeError("File {} contains JSON errors".format(file_path)) from ex

    # Check for molssi_bse_schema key
    if check_bse and 'molssi_bse_schema' not in js:
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

    if file_path.endswith('.bz2'):
        with bz2.open(file_path, 'wt', encoding=_default_encoding) as f:
            json.dump(js, f, indent=2, ensure_ascii=False)
    else:
        with open(file_path, 'w', encoding=_default_encoding) as f:
            json.dump(js, f, indent=2, ensure_ascii=False)


def read_json_basis(file_path):
    """
    Reads generic basis set information from a JSON file

    After reading, the MolSSI BSE schema information is searched for and if not
    found, an exception is raised.

    This function works with basis set metadata, table, element, and json files.

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
    Read a JSON file containing info for all references

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

    This function works with basis set metadata, table, element, and json files.

    Parameters
    ----------
    file_path : str
        Full path to the file to write to. It will be overwritten if it exists
    bs : dict
        Basis set information to write
    """

    _write_plain_json(file_path, sort_basis_dict(bs))


def write_references(file_path, refs):
    """
    Write a dict containing info for all references to a JSON file

    Parameters
    ----------
    file_path : str
        Full path to the file to write to. It will be overwritten if it exists
    refs : dict
        Reference information to write
    """

    _write_plain_json(file_path, sort_references_dict(refs))


def write_metadata(file_path, metadata):
    """
    Reads a file containing the metadata for all the basis sets

    Parameters
    ----------
    file_path : str
        Full path to the file to write to. It will be overwritten if it exists
    metadata : dict
        Metadata information for all basis sets
    """

    _write_plain_json(file_path, sort_basis_dict(metadata))


def get_all_filelist(data_dir):
    """
    Returns a tuple containing the following (as lists)

    0. All metadata files
    1. All table basis files
    2. All element basis files
    3. All component basis files

    The paths to all the files are returned as paths relative to data_dir
    """

    all_meta = []
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

            if basename.endswith('.metadata.json'):
                all_meta.append(fpath)
            elif basename.endswith('.table.json'):
                all_table.append(fpath)
            elif basename.endswith('.element.json'):
                all_element.append(fpath)
            elif basename.endswith('.json'):
                all_component.append(fpath)

    return (all_meta, all_table, all_element, all_component)


def read_notes_file(file_path):
    """
    Returns the contents of a notes file.

    If the notes file does not exist, None is returned
    """

    if not os.path.isfile(file_path):
        return None

    with open(file_path, 'r', encoding=_default_encoding) as f:
        return f.read()

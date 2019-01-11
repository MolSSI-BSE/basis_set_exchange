"""
Functions related to validating JSON files (including against schema)
"""

import jsonschema

from . import api
from . import fileio


def validate_data(file_type, bs_data):
    """
    Validates json basis set data against a schema

    Parameters
    ----------
    file_type : str
        Type of file to read. May be 'component', 'element', 'table', or 'references'
    bs_data:
        Data to be validated

    Raises
    ------
    RuntimeError
        If the file_type is not valid (and/or a schema doesn't exist)
    ValidationError
        If the given file does not pass validation
    FileNotFoundError
        If the file given by file_path doesn't exist
    """

    _valid_schema = ['component', 'element', 'table', 'metadata', 'references']
    if file_type not in _valid_schema:
        raise RuntimeError("{} is not a valid file_type".format(file_type))

    schema = api.get_schema(file_type)
    jsonschema.validate(bs_data, schema)


def validate_file(file_type, file_path):
    """
    Validates a file against a schema

    Parameters
    ----------
    file_type : str
        Type of file to read. May be 'component', 'element', 'table', or 'references'
    file_path:
        Full path to the file to be validated

    Raises
    ------
    RuntimeError
        If the file_type is not valid (and/or a schema doesn't exist)
    ValidationError
        If the given file does not pass validation
    FileNotFoundError
        If the file given by file_path doesn't exist
    """

    file_data = fileio._read_plain_json(file_path, False)
    validate_data(file_type, file_data)

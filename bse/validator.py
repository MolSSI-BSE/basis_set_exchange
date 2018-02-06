"""
Functions related to validating JSON files against schema
"""

import jsonschema
import json
from bse import api


def validate(file_type, file_path):
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

    valid_schema = ['component', 'element', 'table', 'references']
    if file_type not in valid_schema:
        raise RuntimeError("{} is not a valid file_type".format(file_type))

    # We have to manually load the json (to bypass an processing,
    # ie, turning keys into integers
    with open(file_path, 'r') as f:
        to_validate = json.load(f)

    schema = api.get_schema(file_type)

    jsonschema.validate(to_validate, schema)

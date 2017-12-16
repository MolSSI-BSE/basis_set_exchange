import jsonschema
import json
from bse import api

def validate(file_type, file_path):

    # We have to manually load the json (to bypass an processing,
    # ie, turning keys into integers
    with open(file_path, 'r') as f:
        to_validate = json.load(f)

    schema = api.get_schema(file_type)

    jsonschema.validate(to_validate, schema)

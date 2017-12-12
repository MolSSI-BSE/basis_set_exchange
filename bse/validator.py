import jsonschema
import json
from bse import io

def validate(filetype, file_path):

    # We have to manually load the json (to bypass an processing,
    # ie, turning keys into integers
    with open(file_path, 'r') as f:
        to_validate = json.loads(f.read())

    schema = io.read_schema(filetype)

    jsonschema.validate(to_validate, schema)

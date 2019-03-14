'''
Functions for creating skeletons of dictionaries/JSON files
'''

import copy

_skeletons = {
    "component": {
        "molssi_bse_schema": {
            "schema_type": "component",
            "schema_version": "0.1"
        },
        "description": "",
        "data_source": "",
        "elements": {}
    },
    "element": {
        "molssi_bse_schema": {
            "schema_type": "element",
            "schema_version": "0.1"
        },
        "name": "",
        "description": "",
        "elements": {}
    },
    "table": {
        "molssi_bse_schema": {
            "schema_type": "table",
            "schema_version": "0.1"
        },
        "revision_description": "",
        "elements": {}
    },
    "metadata": {
        "molssi_bse_schema": {
            "schema_type": "metadata",
            "schema_version": "0.1"
        },
        "names": [],
        "flags": [],
        "family": "",
        "description": "",
        "role": "",
        "auxiliaries": {}
    }
}


def create_skel(role):
    '''
    Create the skeleton of a dictionary or JSON file

    A dictionary is returned that contains the "molssi_bse_schema"
    key and other required keys, depending on the role

    role can be either 'component', 'element', or 'table'
    '''

    role = role.lower()
    if not role in _skeletons:
        raise RuntimeError("Role {} not found. Should be 'component', 'element', 'table', or 'metadata'")

    return copy.deepcopy(_skeletons[role])

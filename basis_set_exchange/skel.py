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
    "minimal": {
        "molssi_bse_schema": {
            "schema_type": "minimal",
            "schema_version": "0.1"
        },
        "elements": {},
        "function_types": []
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
        "revision_date": "",
        "elements": {}
    },
    "metadata": {
        "molssi_bse_schema": {
            "schema_type": "metadata",
            "schema_version": "0.1"
        },
        "names": [],
        "tags": [],
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
    if role not in _skeletons:
        raise RuntimeError("Role {} not found. Should be 'component', 'element', 'table', or 'metadata'".format(role))

    return copy.deepcopy(_skeletons[role])

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
Conversion of basis sets to QCSchema JSON format
'''

import json
from .. import manip, sort, lut


def write_qcschema(basis):
    '''Converts a basis set to QCSchema JSON

    Note that the output is a string
    '''

    # Uncontract all but SP
    basis = manip.uncontract_spdf(basis, 1, True)
    basis = sort.sort_basis(basis, True)

    basis_name = basis.get('name', 'unknown_basis')
    basis_desc = basis.get('description', '<no description>')
    new_basis = {'schema_name': 'qcschema_basis', 'schema_version': 1, 'name': basis_name, 'description': basis_desc}

    # For the 'center_data' key in the schema
    center_data = {}
    for el, eldata in basis['elements'].items():
        entry_name = lut.element_sym_from_Z(el) + '_' + basis_name

        eldata.pop('references', None)

        if 'electron_shells' in eldata:
            # Fix up some naming
            for sh in eldata['electron_shells']:
                sh.pop('region')
                func = sh.pop('function_type')
                if func == 'gto_spherical':
                    sh['harmonic_type'] = 'spherical'
                else:
                    # Set to cartesian if explicitely cartesian, or if it is an
                    # s or p shell
                    sh['harmonic_type'] = 'cartesian'

        if 'ecp_electrons' in eldata:
            for pot in eldata['ecp_potentials']:
                pot['ecp_type'] = pot['ecp_type'].replace('_ecp', '')

        center_data[entry_name] = eldata

    new_basis['center_data'] = center_data

    return json.dumps(new_basis, indent=2, ensure_ascii=False)

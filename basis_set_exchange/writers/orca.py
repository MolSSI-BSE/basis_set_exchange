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
Conversion of basis sets to ORCA format
'''

from .. import lut, printing
from .gamess_us import write_gamess_us_common


def write_orca_ecp_basis(basis, ecp_elements):
    s = ''
    for z in ecp_elements:
        s += '\n\n'
        data = basis['elements'][z]
        sym = lut.element_sym_from_Z(z).upper()
        max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
        max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=True)

        # Sort lowest->highest
        ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])

        # Could probably be basis['names'][0]-ECP, but seems like special characters
        # would cause problems
        ecp_name = 'NewECP'
        s += '{} {}\n'.format(ecp_name, sym)
        s += '  N_core {}\n'.format(data['ecp_electrons'])
        s += '  lmax {}\n'.format(max_ecp_amchar)

        for pot in ecp_list:
            rexponents = pot['r_exponents']
            gexponents = pot['gaussian_exponents']
            coefficients = pot['coefficients']
            nprim = len(rexponents)

            am = pot['angular_momentum']
            amchar = lut.amint_to_char(am, hij=False)

            # Title line
            s += '  {} {}\n'.format(amchar, nprim)

            # Include an index column
            idx_column = list(range(1, nprim + 1))
            point_places = [4, 12, 27, 36]
            s += printing.write_matrix([idx_column, gexponents, *coefficients, rexponents], point_places)

        s += "end"
    return s


def write_orca(basis):
    '''Converts a basis set to ORCA
    '''

    return write_gamess_us_common(basis, write_orca_ecp_basis)

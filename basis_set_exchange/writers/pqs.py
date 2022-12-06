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
Conversion of basis sets to PQS format
'''

from .. import lut, manip, sort, printing
from .gamess_us import write_gamess_us_ecp_basis


def write_pqs_electron_basis(basis, electron_elements):
    s = ''

    for z in electron_elements:
        data = basis['elements'][z]

        el_sym = lut.element_sym_from_Z(z, normalize=True)
        s += 'FOR        ' + el_sym + "\n"

        for shell in data['electron_shells']:
            exponents = shell['exponents']
            coefficients = shell['coefficients']

            am = shell['angular_momentum']
            amchar = lut.amint_to_char(am, hij=True, use_L=True).upper()

            ncol = len(coefficients) + 1
            point_places = [4 + 8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
            mat = printing.write_matrix([exponents, *coefficients], point_places)

            # Prepend the AM
            mat = amchar + mat[1:]
            s += mat

    return s


def write_pqs(basis):
    '''Converts the basis set to PQS
    '''

    s = ''

    basis = manip.make_general(basis, True)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if electron_elements:
        s += write_pqs_electron_basis(basis, electron_elements)

    # Write out ECP
    if ecp_elements:
        s += '\n\n'
        s += 'Effective core Potentials\n'
        s += '-------------------------\n'
        s += write_gamess_us_ecp_basis(basis, ecp_elements, ecp_block=False)

    return s

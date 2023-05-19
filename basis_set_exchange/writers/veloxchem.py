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
Conversion of basis sets to VeloxChem format
'''

from hashlib import md5

from .. import lut, manip, misc, printing, sort


def write_veloxchem(basis):
    '''Converts a basis set to VeloxChem format
    '''

    s = f'@BASIS_SET {basis["name"]}\n'

    basis = manip.optimize_general(basis, False)

    basis = manip.uncontract_general(basis, False)

    basis = manip.uncontract_spdf(basis, 0, False)

    basis = manip.prune_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, True).upper()
            elname = lut.element_name_from_Z(z).upper()
            cont_string = misc.contraction_string(data)

            s += f'\n! {elname:s}       {cont_string:s}\n'
            s += f'@ATOMBASIS {sym:s}\n'

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                ncol = len(coefficients) + 1
                nprim = len(exponents)
                ngen = len(coefficients)

                am = shell['angular_momentum']
                # use 'hij' convention, where AM=7 is j
                amchar = lut.amint_to_char(am, hij=True)

                s += f'{amchar.upper()}    {nprim:d}    {ngen:d}\n'

                point_places = [2 * i + 16 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=False)

            s += '@END\n'

    md5sum = md5(s.encode('utf-8')).hexdigest()

    return s + md5sum

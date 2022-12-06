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
Conversion of basis sets to FHI-aims format

2021-07-05 Susi Lehtola
'''

from .. import lut, manip, sort, printing


def write_fhiaims(basis):
    '''Converts a basis set to FHI-aims format
    '''

    # Angular momentum type
    types = basis['function_types']
    pure = False if 'gto_cartesian' in types else True

    # Set up
    s = ''
    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 0, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis['elements'][z]

            # FHI-aims defines elements in species default files.
            # The options need to be specified for every element basis.
            s += '''
            # The default minimal basis should not be included
            include_min_basis .false.
            # Use spherical functions?
            pure_gauss {}
            '''.format('.true.' if pure else '.false.')

            sym = lut.element_sym_from_Z(z, True)
            s += '# {} {}\n'.format(sym, basis['name'])

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                ncol = len(coefficients) + 1
                nprim = len(exponents)
                am = shell['angular_momentum']
                assert len(am) == 1

                if nprim == 1:
                    s += 'gaussian {} {} {}\n'.format(am[0], nprim, exponents[0])
                else:
                    s += 'gaussian {} {}\n'.format(am[0], nprim)
                    point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                    s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=False)

    return s

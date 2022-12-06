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
Conversion of basis sets to cp2k format
'''

from .. import lut, sort, misc, printing


def write_cp2k(basis):
    '''Converts a basis set to cp2k format
    '''

    s = ''
    basis = sort.sort_basis(basis, True)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, normalize=True)
            elname = lut.element_name_from_Z(z, normalize=True)
            cont_string = misc.contraction_string(data)

            s += '# {} {} {}\n'.format(elname, basis['name'], cont_string)
            s += '{} {}\n'.format(sym, basis['name'])

            nshells = len(data['electron_shells'])
            s += '    {}\n'.format(nshells)

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                am = shell['angular_momentum']
                min_am = min(am)
                max_am = max(am)
                ncont = len(coefficients)
                ncol = ncont + 1

                nprim = len(exponents)

                # First number is principle quantum number
                # But is not used, according to the documentation
                s += '{} {} {} {}'.format("1", min_am, max_am, nprim)

                if len(am) > 1:
                    for _ in am:
                        s += ' 1'
                else:
                    s += ' ' + str(ncont)
                s += '\n'

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=False)
            s += '\n'

    # Write out ECP
    if ecp_elements:
        bsname = basis['name'].replace(' ', '_') + '_ECP'
        s += '\n\n## Effective core potentials\n'
        s += bsname + '\n'
        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z, normalize=True)
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '{} nelec {}\n'.format(sym, data['ecp_electrons'])

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am).upper()

                if am[0] == max_ecp_am:
                    s += '{} ul\n'.format(sym)
                else:
                    s += '{} {}\n'.format(sym, amchar)

                point_places = [0, 9, 32]
                s += printing.write_matrix([rexponents, gexponents, *coefficients], point_places, convert_exp=False)

        s += 'END ' + bsname + '\n'

    return s

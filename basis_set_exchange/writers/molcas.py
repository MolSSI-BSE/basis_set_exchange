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
Conversion of basis sets to Molcas format
'''

from .. import lut, manip, printing, misc, sort


def write_molcas(basis):
    '''Converts a basis set to Molcas format
    '''

    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    s = ''

    for z, data in basis['elements'].items():
        s += 'Basis set\n'

        has_electron = 'electron_shells' in data
        has_ecp = 'ecp_potentials' in data

        el_name = lut.element_name_from_Z(z).upper()
        el_sym = lut.element_sym_from_Z(z, normalize=True)
        s += '* {}  {}\n'.format(el_name, misc.contraction_string(data))

        # if ECP is present, the line should be "{sym}.ECP /inline"
        ecp_tag = '.ECP' if has_ecp else ''
        s += ' {}{}    / inline\n'.format(el_sym, ecp_tag)

        if has_electron:
            max_am = misc.max_am(data['electron_shells'])

            # number of electrons
            # should be z - number of ecp electrons
            nelectrons = int(z)
            if has_ecp:
                nelectrons -= data['ecp_electrons']

            s += '{:>7}.00   {}\n'.format(nelectrons, max_am)

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                nprim = len(exponents)
                ngen = len(coefficients)

                amchar = lut.amint_to_char(shell['angular_momentum']).upper()
                s += '* {}-type functions\n'.format(amchar)
                s += '{:>6}    {}\n'.format(nprim, ngen)

                s += printing.write_matrix([exponents], [17])

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ngen + 1)]
                s += printing.write_matrix(coefficients, point_places)

        if has_ecp:
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += 'PP, {}, {}, {} ;\n'.format(el_sym, data['ecp_electrons'], max_ecp_am)

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am)
                s += '{};'.format(len(rexponents))

                if am[0] == max_ecp_am:
                    s += ' !  ul potential\n'
                else:
                    s += ' !  {}-ul potential\n'.format(amchar)

                for p in range(len(rexponents)):
                    s += '{},{},{};\n'.format(rexponents[p], gexponents[p], coefficients[0][p])

            s += 'Spectral\n'
            s += 'End of Spectral\n'
            s += '*\n'

        if has_electron:
            # Are there cartesian shells?
            cartesian_shells = set()
            for shell in data['electron_shells']:
                if shell['function_type'] == 'gto_cartesian':
                    for am in shell['angular_momentum']:
                        cartesian_shells.add(lut.amint_to_char([am]))
            if len(cartesian_shells):
                s += 'cartesian {}\n'.format(' '.join(cartesian_shells))

        s += 'End of basis set\n\n'

    return s

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
Conversion of basis sets to Dalton format
'''

from .. import lut, manip, sort, misc, printing


def write_dalton(basis):
    '''Converts a basis set to Dalton format
    '''

    s = '! Basis = {}\n\n'.format(basis['name'])

    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis['elements'][z]
            #sym = lut.element_sym_from_Z(z, True)
            elname = lut.element_name_from_Z(z).upper()
            cont_string = misc.contraction_string(data)

            s += 'a {}\n'.format(z)
            s += '! {}       {}\n'.format(elname, cont_string)

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                ncol = len(coefficients) + 1
                nprim = len(exponents)
                ngen = len(coefficients)

                am = shell['angular_momentum']
                amchar = lut.amint_to_char(am, hij=True)
                s += '! {} functions\n'.format(amchar)

                # Is this a bug in the original EMSL?
                #s += '{}   {}   1.00\n'.format(sym, r, nprim)
                s += '{}    {}    {}\n'.format('H', nprim, ngen)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=False)

    # Write out ECP
    if ecp_elements:
        s += '\n\nECP\n'
        for z in ecp_elements:
            data = basis['elements'][z]
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())
            s += 'a {:3d}\n$\n'.format(int(z))
            s += '{:4d}{:4d}\n'.format(max_ecp_am, data['ecp_electrons'])
            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']
                s += '{:12d}\n'.format(len(rexponents))
                point_places = [0, 9, 32]
                s += printing.write_matrix([rexponents, gexponents, *coefficients],
                                           point_places,
                                           convert_exp=False)
            s += '$\n'
        s += '$ END OF ECP\n'
    return s

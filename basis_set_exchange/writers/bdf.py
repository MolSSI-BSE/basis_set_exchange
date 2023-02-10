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
Conversion of basis sets to BDF format
'''

from .. import lut, manip, printing, sort, misc


def write_bdf(basis):
    '''Converts a basis set to BDF format
    '''

    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    s = ''

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

     # Elements for which we have electron basis or ECP
    all_elements = list(set(electron_elements + ecp_elements))
    all_elements.sort(key=int)

    if electron_elements or ecp_elements:
        for z in all_elements:
            s += "****\n"
            
            #Get element symbol
            symbol = lut.element_sym_from_Z(z, True)
            data = basis['elements'][z]

            if electron_elements and z in electron_elements:
                s += symbol

                max_am = misc.max_am(data['electron_shells'])
                s += '{:>7}   {}\n'.format(z, max_am)

                for shell in data['electron_shells']:
                    exponents = shell['exponents']
                    coefficients = shell['coefficients']
                    nprim = len(exponents)
                    ngen = len(coefficients)

                    amchar = lut.amint_to_char(shell['angular_momentum']).upper()
                    s += '{}    '.format(amchar)
                    s += '{:>3}    {}\n'.format(nprim, ngen)

                    s += printing.write_matrix([exponents], [14])

                    point_places = [7 + 20 * (i - 1) for i in range(1, ngen + 1)]
                    s += printing.write_matrix(coefficients, point_places)

            if ecp_elements and z in ecp_elements:
                s += 'ECP\n'

                data = basis['elements'][z]
                max_ecp_angular_momentum = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
                s += '{}     {}     {}\n'.format(symbol, data['ecp_electrons'], max_ecp_angular_momentum)

                # Sort lowest->highest, then put the highest at the beginning
                ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
                ecp_list.insert(0, ecp_list.pop())

                for pot in ecp_list:
                    rexponents = pot['r_exponents']
                    gexponents = pot['gaussian_exponents']
                    coefficients = pot['coefficients']
                    nprim = len(rexponents)

                    am = pot['angular_momentum']
                    amchar = lut.amint_to_char(am, hij=True).upper()
                    s += '{} potential  {}\n'.format(amchar, str(nprim))

                    point_places = [4, 12, 34]
                    s += printing.write_matrix([rexponents, gexponents, *coefficients], point_places, convert_exp=True)

    s += '****\n'

    return s

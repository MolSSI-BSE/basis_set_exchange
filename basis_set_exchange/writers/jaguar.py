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
Conversion of basis sets to Jaguar format

2021-12-20 Susi Lehtola
'''

from .. import lut, manip, sort, printing


def write_jaguar(basis):
    '''Converts a basis set to Jaguar format
    '''

    basis = manip.uncontract_general(basis, True)
    basis = manip.uncontract_spdf(basis, 1, False)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    types = basis['function_types']
    harm_type = '6D' if 'gto_cartesian' in types else '5D'
    ecp_type = ' ECP' if ecp_elements else ''

    s = 'BASIS {} {}{}\n'.format(basis['name'], harm_type, ecp_type)

    # Electron Basis
    if electron_elements:
        for z in electron_elements:
            data = basis['elements'][z]

            sym = lut.element_sym_from_Z(z, True)
            s += '{}\n'.format(sym)

            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                ncol = len(coefficients) + 1
                nprim = len(exponents)

                am = shell['angular_momentum']
                amchar = lut.amint_to_char(am, hij=True).upper()

                s += '{} 0 {}\n'.format(amchar, nprim)

                point_places = [8 * i + 15 * (i - 1) for i in range(1, ncol + 1)]
                s += printing.write_matrix([exponents, *coefficients], point_places, convert_exp=True)

            if ecp_elements and z in ecp_elements:
                s += '**\n'

                max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
                max_ecp_amchar = lut.amint_to_char([max_ecp_am], hij=False)

                # Sort lowest->highest, then put the highest at the beginning
                ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
                ecp_list.insert(0, ecp_list.pop())

                s += '{} {} {}\n'.format(sym, max_ecp_am, data['ecp_electrons'])
                for pot in ecp_list:
                    rexponents = pot['r_exponents']
                    gexponents = pot['gaussian_exponents']
                    coefficients = pot['coefficients']
                    nprim = len(rexponents)

                    am = pot['angular_momentum']
                    amchar = lut.amint_to_char(am, hij=False)

                    if am[0] == max_ecp_am:
                        s += '{}_AND_UP\n'.format(amchar.upper())
                    else:
                        s += '{}-{}\n'.format(amchar.upper(), max_ecp_amchar.upper())

                    point_places = [0, 9, 32]
                    s += printing.write_matrix([rexponents, gexponents, *coefficients], point_places, convert_exp=True)

            s += '****\n'

    return s

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
Writes basis set in Molpro system library format

Written by Susi Lehtola, 2020
(based on Ben Pritchard's Molpro input code)
'''

from .. import lut, manip, misc, sort
from .common import find_range, reshape


def write_libmol(basis):
    '''Converts a basis set to Molpro system library format
    '''

    # Uncontract all, and make as generally-contracted as possible
    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, True)

    # Start out with angular momentum type
    types = basis['function_types']
    harm_type = 'cartesian' if 'gto_cartesian' in types else 'spherical'
    s = harm_type + '\n'

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    if electron_elements:
        # basis set starts with a string
        s += 'basis={\n'

        # Electron Basis
        for z in electron_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            for shell in data['electron_shells']:
                exponents = shell['exponents']
                coefficients = shell['coefficients']
                am = shell['angular_momentum']
                amchar = lut.amint_to_char(am).lower()

                nprim = len(exponents)
                ncontr = len(coefficients)

                # Collect ranges and coefficients
                ranges = ''
                print_data = exponents.copy()
                for c in coefficients:
                    first, last = find_range(c)
                    ranges += ' {}.{}'.format(first + 1, last + 1)
                    print_data += c[first:last + 1]

                # Print block entry
                s += '{} {} {} : {} {}{}\n'.format(sym, amchar, basis['name'], nprim, ncontr, ranges)
                # Comment
                s += '{} {} converted by Basis Set Exchange\n'.format(lut.element_name_from_Z(z),
                                                                      misc.contraction_string(data))

                # Output data has 5 entries per row
                print_data = reshape(print_data, 5)
                for d in print_data:
                    s += ' '.join(d) + '\n'

    # Write out ECP
    if ecp_elements:
        s += '\n\n! Effective core Potentials\n'

        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).lower()
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            # Collect data for the printout
            numdata = 0
            print_blocks = []
            for pot in ecp_list:
                rexp = pot['r_exponents']
                gexp = pot['gaussian_exponents']
                coef = pot['coefficients']

                block = []
                for i in range(len(rexp)):
                    block += [str(rexp[i]), gexp[i], coef[0][i]]
                print_blocks.append(block)
                # Data block printout will have this many entries
                numdata += 3 * len(rexp) + 1

            # Spin-orbit ECPs are not supported by the BSE schema(?)
            nspinorbit = 0
            # Print out header
            s += '{} ECP : {} {} {} {}\n'.format(sym, data['ecp_electrons'], max_ecp_am, nspinorbit, numdata)
            s += 'ECP for {} converted by Basis Set Exchange\n'.format(basis['name'])
            for b in print_blocks:
                # Print number of terms
                s += '{} '.format(len(b) // 3)
                # Each line has 6 ECP data
                pb = reshape(b, 6)
                for d in range(len(pb)):
                    if d > 0:
                        # Pad with two spaces to get the entry to align
                        s += '  '
                    # Add the data
                    s += ' '.join(pb[d]) + '\n'
    return s

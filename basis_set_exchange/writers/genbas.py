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
Conversion of basis sets to cfour/aces2/genbas format
'''

import math
from .. import lut, manip, sort, printing


def _cfour_exp(e):
    '''Formats an exponent for CFour'''
    return e.replace('E', 'D') + ' '


def _cfour_coef(c):
    '''Formats a coefficient for CFour'''
    return c.replace('E', 'D') + ' '


def _aces_exp(e):
    '''Formats an exponent for AcesII'''

    e = float(e)
    # Some basis sets have negative exponents???
    mag = int(math.log(abs(e), 10))

    mag = max(mag, 1)

    # Make room for the negative sign
    if e < 0.0:
        mag += 1

    # Number of decimal places to show
    ndec = min(7, 14 - 2 - mag)

    fmtstr = '{{:14.{}f}}'.format(ndec)
    s = fmtstr.format(e)

    # Trim a single trailing zero if there is one
    # and our string takes up all 14 characters
    if s[0] != ' ' and s[-1] == '0':
        s = ' ' + s[:-1]

    return s


def _aces_coef(c):
    '''Formats a coefficient for AcesII'''
    c = float(c)
    return '{:10.7f} '.format(c)


def _print_columns(data, ncol):
    s = ''
    for i in range(0, len(data), ncol):
        s += ''.join(data[i:i + ncol]) + '\n'
    return s


def _write_genbas_internal(basis, exp_formatter, coef_formatter):
    # Uncontract all, then make general
    basis = manip.make_general(basis, False, True)
    basis = sort.sort_basis(basis, False)

    # Elements for which we have electron basis
    electron_elements = [k for k, v in basis['elements'].items() if 'electron_shells' in v]

    # Elements for which we have ECP
    ecp_elements = [k for k, v in basis['elements'].items() if 'ecp_potentials' in v]

    s = '\n'

    if electron_elements:
        # Electron Basis
        for z in electron_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            nshell = len(data['electron_shells'])

            s += '{}:{}\n'.format(sym, basis['name'])
            s += basis['description'] + '\n'
            s += '\n'
            s += '{:>3}\n'.format(nshell)

            s_am = ''
            s_ngen = ''
            s_nprim = ''
            for sh in data['electron_shells']:
                s_am += '{:>5}'.format(sh['angular_momentum'][0])
                s_ngen += '{:>5}'.format(len(sh['coefficients']))
                s_nprim += '{:>5}'.format(len(sh['exponents']))

            s += s_am + '\n'
            s += s_ngen + '\n'
            s += s_nprim + '\n'
            s += '\n'

            for shell in data['electron_shells']:
                exponents = [exp_formatter(x) for x in shell['exponents']]
                coefficients = [[coef_formatter(x) for x in y] for y in shell['coefficients']]
                coefficients = list(map(list, zip(*coefficients)))

                s += _print_columns(exponents, 5) + '\n'
                for c in coefficients:
                    s += _print_columns(c, 7)
                s += '\n'

    # Write out ECP
    if ecp_elements:
        s += '\n\n! Effective core Potentials\n'

        for z in ecp_elements:
            data = basis['elements'][z]
            sym = lut.element_sym_from_Z(z).upper()
            max_ecp_am = max([x['angular_momentum'][0] for x in data['ecp_potentials']])
            max_ecp_amchar = lut.amint_to_char([max_ecp_am]).lower()

            # Sort lowest->highest, then put the highest at the beginning
            ecp_list = sorted(data['ecp_potentials'], key=lambda x: x['angular_momentum'])
            ecp_list.insert(0, ecp_list.pop())

            s += '*\n'
            s += '{}:{}\n'.format(sym, basis['name'])
            s += '# ' + basis['description'] + '\n'
            s += '*\n'
            s += '    NCORE = {}    LMAX = {}\n'.format(data['ecp_electrons'], max_ecp_am)

            for pot in ecp_list:
                rexponents = pot['r_exponents']
                gexponents = pot['gaussian_exponents']
                coefficients = pot['coefficients']

                am = pot['angular_momentum']
                amchar = lut.amint_to_char(am).lower()

                if am[0] == max_ecp_am:
                    s += '{}\n'.format(amchar)
                else:
                    s += '{}-{}\n'.format(amchar, max_ecp_amchar)

                point_places = [6, 18, 25]
                s += printing.write_matrix([*coefficients, rexponents, gexponents], point_places)
                #for p in range(len(rexponents)):
                #    s += '{}  {}  {};\n'.format(gexponents[p], rexponents[p], coefficients[0][p])
            s += '*\n'
    return s


def write_cfour(basis):
    '''Converts a basis set to cfour
    '''

    # March 2019
    # Format determined from http://slater.chemie.uni-mainz.de/cfour/index.php?n=Main.NewFormatOfAnEntryInTheGENBASFile

    return _write_genbas_internal(basis, _cfour_exp, _cfour_coef)


def write_aces2(basis):
    '''Converts a basis set to cfour
    '''

    # March 2019
    # Format determined from http://slater.chemie.uni-mainz.de/cfour/index.php?n=Main.OldFormatOfAnEntryInTheGENBASFile

    return _write_genbas_internal(basis, _aces_exp, _aces_coef)

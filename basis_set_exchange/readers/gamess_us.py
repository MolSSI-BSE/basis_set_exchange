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
GAMESS US parser

2021-11-17 Susi Lehtola
'''

import re
from .. import lut, manip
from . import helpers

element_block_re = re.compile(r'^\s*([a-zA-Z]+)\s*$')
shell_block_re = re.compile(r'^\s*([SPDFGHIKLMN])\s+(\d+)\s*$')
contraction_re = re.compile(r'^\s*(\d+)\s+({0})\s+({0})\s*$'.format(helpers.floating_re_str))

# e.g. RB-ECP GEN    28    3
ecp_block_re = re.compile(r'^\s*([a-zA-Z]+)-ECP GEN\s+(\d+)\s+(\d+)\s*$')
ecp_shell_re = re.compile(r'^\s*(\d+)\s+-----\s+([a-zA-Z])-([a-zA-Z]+)\s+potential\s+-----\s*$')
ecp_entry_re = re.compile(r'^\s*({0})\s+(\d)\s+({0})\s*$'.format(helpers.floating_re_str))


def _parse_electron_lines(basis_lines, bs_data):
    element_name = helpers.parse_line_regex(element_block_re, basis_lines[0])
    element_Z = lut.element_Z_from_name(element_name, as_str=True)
    element_data = manip.create_element_data(bs_data, element_Z, 'electron_shells')

    iline = 1
    while iline < len(basis_lines) and shell_block_re.match(basis_lines[iline]):
        shell_am_char, nprim = helpers.parse_line_regex(shell_block_re, basis_lines[iline])
        shell_am = lut.amchar_to_int(shell_am_char)
        func_type = lut.function_type_from_am(shell_am, 'gto', 'spherical')
        iline += 1

        exponents = []
        coefficients = []
        for iprim in range(nprim):
            primidx, expn, coeff = helpers.parse_line_regex(contraction_re, basis_lines[iline])
            assert primidx == iprim + 1
            iline += 1
            if float(coeff) != 0.0:
                exponents.append(expn)
                coefficients.append(coeff)

        shell = {
            'function_type': func_type,
            'region': '',
            'angular_momentum': shell_am,
            'exponents': exponents,
            'coefficients': [coefficients]
        }
        element_data['electron_shells'].append(shell)


def _parse_ecp_lines(basis_lines, bs_data):
    iline = 0
    while iline < len(basis_lines) and ecp_block_re.match(basis_lines[iline]):
        element_sym, ecp_electrons, lmax = helpers.parse_line_regex(ecp_block_re, basis_lines[iline])
        iline += 1

        element_Z = lut.element_Z_from_sym(element_sym, as_str=True)
        element_data = manip.create_element_data(bs_data, element_Z, 'ecp_potentials')
        element_data['ecp_electrons'] = ecp_electrons

        while iline < len(basis_lines) and ecp_shell_re.match(basis_lines[iline]):
            nprim, am, _ = helpers.parse_line_regex(ecp_shell_re, basis_lines[iline])
            am = lut.amchar_to_int(am)
            iline += 1

            gexp = []
            rexp = []
            coeff = []
            for iprim in range(nprim):
                c, r, z = helpers.parse_line_regex(ecp_entry_re, basis_lines[iline])
                iline += 1
                if float(c) != 0.0:
                    gexp.append(z)
                    coeff.append(c)
                    rexp.append(r)

            ecp_pot = {
                'angular_momentum': am,
                'ecp_type': 'scalar_ecp',
                'r_exponents': rexp,
                'gaussian_exponents': gexp,
                'coefficients': [coeff]
            }
            element_data['ecp_potentials'].append(ecp_pot)


def read_gamess_us(basis_lines):
    '''Reads GAMESS US file data and converts it to a dictionary with the
       usual BSE fields

       Note that the genbas format does not store all the fields we
       have, so some fields are left blank
    '''

    basis_lines = helpers.prune_lines(basis_lines, '!#$', prune_blank=True)

    bs_data = {}
    other_data = {}

    # split into element blocks
    # each block may be electron shells or ECP
    element_blocks = helpers.partition_lines(basis_lines, element_block_re.match)
    ecp_blocks = helpers.partition_lines(basis_lines, ecp_block_re.match)

    for element_lines in element_blocks:
        _parse_electron_lines(element_lines, bs_data)
    for ecp_lines in ecp_blocks:
        _parse_ecp_lines(ecp_lines, bs_data)

    return bs_data, other_data

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
Reader for the genbas format
'''

import re
from .. import lut, misc, manip
from . import helpers
from .turbomole import _parse_ecp_potential_lines

element_block_re = re.compile(r'^([a-zA-Z]{1,3}):(.*)$')
ecp_block_re = re.compile(r'ncore\s*=\s*(\d+)\s+lmax\s*=\s*(\d+)\s*$', flags=re.IGNORECASE)


def _parse_electron_lines(basis_lines, bs_data):
    # Line 0: element, basis name
    # Line 1: comment
    # Line 2: blank
    # Line 3: nshell (actually line 2 now)

    element_sym, _ = helpers.parse_line_regex(element_block_re, basis_lines[0])
    element_Z = lut.element_Z_from_sym(element_sym, as_str=True)

    element_data = manip.create_element_data(bs_data, element_Z, 'electron_shells')

    basis_lines = basis_lines[2:]

    # Line 2 (now line 0) should be blank
    basis_lines = helpers.remove_expected_line(basis_lines)

    nshell = helpers.parse_line_regex(r'^(\d+)$', basis_lines[0], "Nshell integer")

    # Read in
    # 1. AM for each shell
    # 2. Nprim for each shell
    # These function calls strip off lines that have already been read
    shell_ams, basis_lines = helpers.read_n_integers(basis_lines[1:], nshell, True)
    shell_ngens, basis_lines = helpers.read_n_integers(basis_lines, nshell, True)
    shell_nprims, basis_lines = helpers.read_n_integers(basis_lines, nshell, True)

    # Loop over all shells
    for shell_idx in range(nshell):

        shell_am = [shell_ams[shell_idx]]
        nprim = shell_nprims[shell_idx]
        ngen = shell_ngens[shell_idx]

        func_type = lut.function_type_from_am(shell_am, 'gto', 'spherical')

        # Read in exponents and coefficients
        # We know the dimensions of the coefficient matrix. That matrix
        # also has rows which may span multiple columns

        # The next line should be blank (before exponents)
        basis_lines = helpers.remove_expected_line(basis_lines)
        exponents, basis_lines = helpers.read_n_floats(basis_lines, nprim)

        # Next line should be blank (between exponents and coefficients)
        basis_lines = helpers.remove_expected_line(basis_lines)

        coefficients, basis_lines = helpers.parse_fixed_matrix(basis_lines, nprim, ngen)
        coefficients = misc.transpose_matrix(coefficients)

        shell = {
            'function_type': func_type,
            'region': '',
            'angular_momentum': shell_am,
            'exponents': exponents,
            'coefficients': coefficients
        }

        element_data['electron_shells'].append(shell)

    # Remaining lines should either be blank or '*'
    basis_lines = helpers.prune_lines(basis_lines, '*')
    if basis_lines:
        raise RuntimeError("Found extra lines after element block: " + str(basis_lines))


def _parse_ecp_lines(basis_lines, bs_data):
    # Line 0: element, basis name
    # Line 1: comment, but starts with #, so it was removed
    # Line 2: *
    # Line 3: ncore lmax
    #element_sym, _ = helpers.parse_line_regex(element_block_re, basis_lines[0])
    #element_Z = str(lut.element_Z_from_sym(element_sym))

    #element_data = manip.create_element_data(bs_data, element_Z, 'ecp_potentials')

    # We can use the turbomole parser for ECP.
    # However, needs to be fixed
    # We need to remove the * line
    basis_lines = helpers.remove_expected_line(basis_lines, '*', 1)

    # Also, remove all the other '*' lines (genbas seems to have some extra)
    basis_lines = helpers.prune_lines(basis_lines, '*')

    # Replace the colon on the first line with a space
    basis_lines[0] = basis_lines[0].replace(':', ' ', 1)

    # Now we can use the turbomole version
    _parse_ecp_potential_lines(basis_lines, bs_data)


def read_genbas(basis_lines):
    '''Reads genbas-formatted file data and converts it to a dictionary with the
       usual BSE fields

       This also handles cfour and acesII, which differ only
       in how floating-point numbers are written

       Note that the genbas format does not store all the fields we
       have, so some fields are left blank
    '''

    # We leave in blank lines - they are significant
    # Leave strip_end_blanks to True though
    basis_lines = helpers.prune_lines(basis_lines, '!#', prune_blank=False)

    bs_data = {}
    other_data = {}

    # split into element blocks
    # each block may be electron shells or ECP
    element_blocks = helpers.partition_lines(basis_lines, element_block_re.match, min_after=1, min_size=4)

    for element_lines in element_blocks:
        if any(ecp_block_re.match(l) for l in element_lines):
            _parse_ecp_lines(element_lines, bs_data)
        else:
            _parse_electron_lines(element_lines, bs_data)

    return bs_data, other_data

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
Reader for Molpro basis as user input

Written by Susi Lehtola, 2020
'''

import re
import regex
from .. import lut, manip
from . import helpers

# Basis entry start: 'basis={' allowing whitespace
basis_start_re = re.compile(r'^\s*?basis\s*?=\s*?{\s*?$')
# Basis ends with '}' allowing whitespace
basis_end_re = re.compile(r'^\s*?}\s*?$')
# Shell entry: 'am,element,expn1,expn2,...' allowing whitespace
element_shell_re = regex.compile(
    r'^\s*?(?P<am>[spdfghikSPDFGHIK])\s*?,?\s*?(?P<sym>\w+)\s*?(?:,?\s*(?P<exp>{})\s*)+\s*?$'.format(
        helpers.floating_re_str))
# Contraction entry: 'am,element,expn1,expn2,...' allowing whitespace
contraction_re = regex.compile(r'^\s*?c\s*?,?\s*?(?P<start>\d+).(?P<end>\d+)\s*?(?:,?\s*(?P<coeff>{})\s*)+\s*?$'.format(
    helpers.floating_re_str))

# ECP entry: ECP, symbol, number of electrons in ECP, lmax
ecp_re = regex.compile(r'^\s*ECP\s*,\s*(?P<sym>\w+)\s*,\s*(?P<ncore>\d+)\s*,\s*(?P<lmax>\d+)\s*;\s*$')
# ECP block start: number of terms
ecp_block_re = re.compile(r'^\s*(\d+)\s*;')
# ECP data: rexp expn coeff
ecp_data_re = re.compile(r'^\s*(\d+)\s*,\s*({0})\s*,\s*({0})\s*;\s*'.format(helpers.floating_re_str))

# Function type: spherical by default
_func_type = 'gto_spherical'


def _read_shell(basis_lines, bs_data, iline):
    '''Reads a shell from the input'''

    # Read the shell entry
    shell = helpers.parse_line_regex_dict(element_shell_re, basis_lines[iline], 'am, element, exps')

    # Angular momentum
    assert (len(shell['am']) == 1)
    shell_am = lut.amchar_to_int(shell['am'][0])
    # Element
    assert (len(shell['sym']) == 1)
    element_sym = shell['sym'][0]
    # Exponents
    exponents = [expn.replace('D','E') for expn in shell['exp']]

    # Number of primitives
    nprim = len(exponents)
    assert (nprim > 0)

    # Create entry
    element_Z = lut.element_Z_from_sym(element_sym, as_str=True)
    if element_Z not in bs_data:
        element_data = manip.create_element_data(bs_data, element_Z, 'electron_shells')
    else:
        element_data = bs_data[element_Z]

    # Read in contractions
    coefficients = []
    while True:
        iline += 1
        if contraction_re.match(basis_lines[iline]):
            # We have another contraction
            contr = helpers.parse_line_regex_dict(contraction_re, basis_lines[iline], 'contraction')
            # Start and end exponent
            assert (len(contr['start']) == 1)
            assert (len(contr['end']) == 1)
            start = contr['start'][0]
            end = contr['end'][0]
            # Contraction coefficients
            cc = [coeff.replace('D','E') for coeff in contr['coeff']]

            # Check number of primitives in contraction
            ncontr = end - start + 1
            assert (len(cc) == ncontr)

            # Pad coefficients with zeros
            if start > 1:
                cc = ['0.0' for _ in range(1, start)] + cc
            if end < nprim:
                cc = cc + ['0.0' for _ in range(end, nprim)]

            assert (len(cc) == nprim)
            # Add to contraction
            coefficients.append(cc)
        else:
            # Stop reading contractions
            break

    # Function type
    func_type = 'gto' if shell_am[0] < 2 else _func_type
    # Store the data
    shell = {
        'function_type': func_type,
        'region': '',
        'angular_momentum': shell_am,
        'exponents': exponents,
        'coefficients': coefficients
    }
    element_data['electron_shells'].append(shell)

    return iline


def _read_ecp(basis_lines, bs_data, iline):
    '''Reads an ECP from the input'''
    # Read the ECP entry
    shell = helpers.parse_line_regex_dict(ecp_re, basis_lines[iline], 'ECP, symbol, ncore, lmax')
    element_sym = shell['sym'][0]
    ncore = shell['ncore'][0]
    lmax = shell['lmax'][0]

    # ECP blocks
    ecp_blocks = []
    for l in range(-1, lmax):
        # Read the number of terms in the block
        iline += 1
        nterms = helpers.parse_line_regex(ecp_block_re, basis_lines[iline], 'nterms')
        ecp_block = []
        for i in range(nterms):
            iline += 1
            ecp_block.append(helpers.parse_line_regex(ecp_data_re, basis_lines[iline], 'rexp, expn, coeff'))
        ecp_blocks.append(ecp_block)

    # Create entry
    element_Z = lut.element_Z_from_sym(element_sym, as_str=True)
    if element_Z not in bs_data or 'ecp_potentials' not in bs_data[element_Z]:
        element_data = helpers.create_element_data(bs_data, element_Z, 'ecp_potentials')
    else:
        element_data = bs_data[element_Z]

    # Store data
    element_data['ecp_electrons'] = ncore
    for il in range(len(ecp_blocks)):
        ecp_l = lmax if il == 0 else il - 1
        r_exp = [entry[0].replace('D','E') for entry in ecp_blocks[il]]
        g_exp = [entry[1].replace('D','E') for entry in ecp_blocks[il]]
        coeff = [entry[2].replace('D','E') for entry in ecp_blocks[il]]
        ecp_pot = {
            'angular_momentum': [ecp_l],
            'ecp_type': 'scalar_ecp',
            'r_exponents': r_exp,
            'gaussian_exponents': g_exp,
            'coefficients': [coeff]
        }
        element_data['ecp_potentials'].append(ecp_pot)
    return iline


def _parse_lines(basis_lines, bs_data):
    '''Parses lines representing all the electron shells for a single element

    Resulting information is stored in bs_data
    '''

    # Read the data one line at a time
    iline = 0
    while iline < len(basis_lines):
        if element_shell_re.match(basis_lines[iline]):
            iline = _read_shell(basis_lines, bs_data, iline)
        elif ecp_re.match(basis_lines[iline]):
            iline = _read_ecp(basis_lines, bs_data, iline)
        else:
            iline += 1


def read_molpro(basis_lines):
    '''Reads basis set from Molpro user input data and converts it to a
       dictionary with the usual BSE fields

       Note that the Molpro user input format does not store all the
       fields we have, so some fields are left blank

    '''

    # Removes comments
    basis_lines = helpers.prune_lines(basis_lines, '!*')

    bs_data = {}
    other_data = {}

    # Go through input and check basis type
    _func_type = 'gto_spherical'
    for line in basis_lines:
        if line.strip().lower() == 'spherical':
            _func_type = 'gto_spherical'
        elif line.strip().lower() == 'cartesian':
            _func_type = 'gto_cartesian'

    # Empty file?
    if not basis_lines:
        return bs_data

    _parse_lines(basis_lines, bs_data)

    return bs_data, other_data

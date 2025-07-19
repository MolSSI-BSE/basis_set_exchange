# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#                    2025 Susi Lehtola
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
Crystal format parser

Written by Susi Lehtola, 2020-2025
'''

import re
from .. import manip, lut
from . import helpers

# Element entry starts out with two integers
element_re = re.compile(r'^([\d]{1,3})\s+([\d]+)$')
# The shell definition has three integers and two (potentially floating point, maybe integer) numbers
shell_re = re.compile(r'^([\d]+)\s+([\d]+)\s+([\d]+)\s+({0}|[\d]+)\s+({0}|[\d]+)$'.format(helpers.floating_re_str))
# ECP definition: ZNUC and six integers for number of terms.
ecp_re = re.compile(r'^({0}|[\d]+)\s+([\d]+)\s+([\d]+)\s+([\d]+)\s+([\d]+)\s+([\d]+)\s+([\d]+)$'.format(
    helpers.floating_re_str))
# ECP entry: expn coeff rexp
ecp_entry_re = re.compile(r'^({0})\s+({0})\s+(\d)$'.format(helpers.floating_re_str))
# Terminator
terminator_re = re.compile(r'^99\s+0$')

def _get_element_ecp(basis_lines):
    '''Determines the element and if an ECP is used'''
    # See pg 24 in https://www.crystal.unito.it/Manuals/crystal17.pdf
    # First line is "{element} {number of shells}"
    NAT = int(basis_lines[0].split()[0])
    element_Z = NAT % 100
    # ECPs are used only in this range
    ecp = (NAT > 200 and NAT <= 1000)

    return element_Z, ecp


def _parse_electron_lines(basis_lines, bs_data):
    '''Parses lines representing all the electron shells for a single element

    Resulting information is stored in bs_data
    '''

    # Get element and use of ecp
    element_Z, ecp = _get_element_ecp(basis_lines)

    # Get symbol
    element_data = manip.create_element_data(bs_data, str(element_Z), 'electron_shells')

    # After that come the shells.
    shell_blocks = helpers.partition_lines(basis_lines[1:], shell_re.match)
    for sh_lines in shell_blocks:
        # Skip any blocks that don't have the correct structure
        if not shell_re.match(sh_lines[0]):
            continue

        # Shell starts with five integers
        ityb, raw_shell_am, nprim, formal_charge, scaling_factors = helpers.parse_line_regex(
            shell_re, sh_lines[0], "ityb, lat, ng, che, scal")
        assert (ityb == 0)  # other choices 1 or 2 are Pople STO-nG and 3(6)-21G

        # Parse angular momentum
        if raw_shell_am == 0:
            shell_am = [0]
        elif raw_shell_am == 1:
            # SP shell
            shell_am = [0, 1]
        else:
            # offset by 1
            shell_am = [raw_shell_am - 1]

        # CRYSTAL uses a spherical basis
        func_type = lut.function_type_from_am(shell_am, 'gto', 'spherical')

        # Handle scaling factor
        scaling_factor = float(scaling_factors)**2
        has_scaling = scaling_factor != 1.0

        # How many columns of coefficients do we have? Crystal
        # doesn't support general contractions, so only >1 if you have
        # a fused shell
        ngen = len(shell_am)

        # Now read the exponents and coefficients
        exponents, coefficients = helpers.parse_primitive_matrix(sh_lines[1:nprim + 1], nprim, ngen)

        # If there is a scaling factor, apply it
        # But we keep track of some significant-figure type stuff (as best we can)
        if has_scaling:
            new_exponents = []
            for ex in exponents:
                ex = float(ex) * scaling_factor
                ex = '{:.16E}'.format(ex)

                # Trim useless zeroes
                ex_splt = ex.split('E')
                ex = ex_splt[0].rstrip('0')
                if ex[-1] == '.':  # Stripped all the zeroes...
                    ex += '0'
                ex += 'E' + ex_splt[1]
                new_exponents.append(ex)

            exponents = new_exponents

        shell = {
            'function_type': func_type,
            'region': '',
            'angular_momentum': shell_am,
            'exponents': exponents,
            'coefficients': coefficients
        }

        element_data['electron_shells'].append(shell)


def _parse_ecp_lines(basis_lines, bs_data):
    '''Parses lines representing the ECP data for an element

    Resulting information is stored in bs_data
    '''

    # Get element and use of ecp
    element_Z, ecp = _get_element_ecp(basis_lines)
    element_data = manip.create_element_data(bs_data, str(element_Z), 'ecp_potentials')

    ecp_sections = helpers.partition_lines(basis_lines, ecp_re.match)
    for ecp_lines in ecp_sections:
        # Skip any blocks that don't have the correct structure
        if not ecp_re.match(ecp_lines[0]):
            continue

        # First line is information about the ECP
        Znuc, M, M0, M1, M2, M3, M4 = helpers.parse_line_regex(ecp_re, ecp_lines[0], 'Znuc, M, M0, M1, M2, M3, M4')

        # Number of electrons *in* the ECP
        element_data['ecp_electrons'] = element_Z - int(float(Znuc))

        # Read in the records
        ecp_records = [
            helpers.parse_line_regex(ecp_entry_re, ecp_lines[1 + iline], 'ALFKL, CGKL, NKL')
            for iline in range(M + M0 + M1 + M2 + M3 + M4)
        ]

        # Collect the results
        def get_data(records):
            '''Extracts the data from the ecp record'''
            r_exp = [r[2]+2 for r in records] # CRYSTAL has the bare exponent but BSE appears to store the exponents assuming a r^{-2} prefactor
            g_exp = [r[0] for r in records]
            coeff = [r[1] for r in records]

            return r_exp, g_exp, coeff

        M_arr = [M, M0, M1, M2, M3, M4]
        offset = 0
        for idx, mdata in enumerate(M_arr):
            if mdata > 0:
                # We have an entry, extract it from the read-in records
                r_exp, g_exp, coeff = get_data(ecp_records[offset:offset + mdata])
                # increment offset
                offset += mdata

                if idx == 0:
                    # this is the maximum angular momentum projector in the BSE syntax
                    M_am = M_arr[1:]
                    assert len(M_am) == 5
                    am_val = len(M_am)-1
                    while M_am[am_val] == 0:
                        am_val -= 1
                    ecp_am = [am_val + 1]
                else:
                    # These terms come with a projection operator with am
                    ecp_am = [idx - 1]

                ecp_pot = {
                    'angular_momentum': ecp_am,
                    'ecp_type': 'scalar_ecp',
                    'r_exponents': r_exp,
                    'gaussian_exponents': g_exp,
                    'coefficients': [coeff]  # BSE expects coefficients in a double array
                }
                element_data['ecp_potentials'].append(ecp_pot)


def read_crystal(basis_lines):
    '''Reads Crystal-formatted file data and converts it to a dictionary
       with the usual BSE fields

       Note that the Crystal format does not store all the fields we
       have, so some fields are left blank
    '''

    # Removes comments
    basis_lines = helpers.prune_lines(basis_lines, '!')

    bs_data = {}
    other_data = {}

    # Empty file?
    if not basis_lines:
        return bs_data

    # split into element sections (may be electronic or ecp)
    element_sections = helpers.partition_lines(basis_lines, element_re.match)
    for es in element_sections:
        # Check for termination
        if terminator_re.match(es[0]):
            break

        element_Z, ecp = _get_element_ecp(es)
        _parse_electron_lines(es, bs_data)
        if ecp:
            _parse_ecp_lines(es, bs_data)

    return bs_data, other_data

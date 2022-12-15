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
Reader for the VeloxChem format
'''

import re
from hashlib import md5

from .. import lut, manip
from . import helpers

# Lines beginning a shell can be:
# {shell_am} {nprim} {ncont}
# where shell_am is one of SPDFGHIJKLMNOQRTUVWXYZABCE (use 'hij' convention, i.e. J for AM=7)
shell_begin_re = re.compile(r'^([SPDFGHIJKLMNOQRTUVWXYZABCE])\s+(\d+)\s+(\d+)$')


def _parse_electron_lines(basis_lines, bs_data):
    '''Parses lines representing all the electron shells for all elements

    Resulting information is stored in bs_data
    '''
    # fix common spelling mistakes
    basis_lines = [re.sub('PHOSPHOROUS', 'PHOSPHORUS', line) for line in basis_lines]
    # A little bit of a hack here
    # If we find the start of an element, remove all the following comment lines
    new_basis_lines = []
    i = 0
    while i < len(basis_lines):
        if _line_begins_element(basis_lines[i]):
            new_basis_lines.append(basis_lines[i])
            i += 1
            while basis_lines[i].startswith('!'):
                i += 1
        else:
            new_basis_lines.append(basis_lines[i])
            i += 1

    basis_lines = helpers.prune_lines(new_basis_lines, '$')

    # Now split out all the element blocks
    element_blocks = helpers.partition_lines(basis_lines, _line_begins_element, min_size=3)

    # For each block, split out all the shells
    for el_lines in element_blocks:
        # Figure out which type of block this is (does it start with 'a ' or a comment
        header = el_lines[0].lower()
        if header.startswith('a '):
            element_Z = helpers.parse_line_regex(r'a +(\d+) *$', header, "a {element_z}", convert_int=False)
        elif header.startswith('!'):
            element_name = helpers.parse_line_regex(element_begin_re, header, '! {element_name}')
            element_Z = lut.element_Z_from_name(element_name, as_str=True)
        else:
            raise RuntimeError("Unable to parse block in dalton: header line is \"{}\"".format(header))

        element_data = manip.create_element_data(bs_data, element_Z, 'electron_shells')
        el_lines.pop(0)

        # Remove all the rest of the comment lines
        el_lines = helpers.prune_lines(el_lines, '!')

        # Now partition again into blocks of shells for this element
        shell_blocks = helpers.partition_lines(el_lines, lambda x: shell_begin_re.match(x))

        # Shells are written in increasing angular momentum
        shell_am = 0

        for sh_lines in shell_blocks:
            nprim, ngen = helpers.parse_line_regex(shell_begin_re, sh_lines[0], 'nprim, ngen')
            bas_lines = sh_lines[1:]
            # fix for split over newline
            if nprim > 0 and bas_lines:
                num_line_splits = len(sh_lines[1:]) // nprim
                if num_line_splits * nprim == len(sh_lines[1:]):
                    bas_lines = [
                        ' '.join([sh_lines[1 + num_line_splits * i + offset] for offset in range(num_line_splits)])
                        for i in range(nprim)
                    ]
            exponents, coefficients = helpers.parse_primitive_matrix(bas_lines, nprim=nprim, ngen=ngen)

            func_type = lut.function_type_from_am([shell_am], 'gto', 'spherical')

            shell = {
                'function_type': func_type,
                'region': '',
                'angular_momentum': [shell_am],
                'exponents': exponents,
                'coefficients': coefficients
            }

            element_data['electron_shells'].append(shell)
            shell_am += 1


def read_veloxchem(basis_lines):
    '''Reads VeloxChem-formatted file data and converts it to a dictionary with the
       usual BSE fields.
    '''

    bs_data = {}

    # empty file?
    if not basis_lines:
        return bs_data

    # read in expected MD5 checksum
    expected_md5sum = basis_lines.pop().strip()

    # find first line of basis set information
    idxs = [i for i, line in enumerate(basis_lines) if line.startswith('@BASIS_SET')]
    if len(idxs) > 1:
        raise RuntimeError("Multiple @BASIS_SET lines found. There should be only one")
    idx = idxs[0]

    # recompute MD5 checksum
    computed_md5sum = md5(("".join(basis_lines[idx:])).encode('utf-8')).hexdigest()

    # validate MD5 checksum
    if computed_md5sum != expected_md5sum:
        raise RuntimeError("Computed and expected MD5 checksums for basis set differ.")

    # prune comments and blank lines
    basis_lines = helpers.prune_lines(basis_lines, skipchars='!', prune_blank=True, strip_end_blanks=True)

    # get atom-by-atom lines: between @ATOMBASIS and @END markers
    idxs_atombasis = [(i, line.split()[1]) for i, line in enumerate(basis_lines) if line.startswith('@ATOMBASIS')]
    idxs_end = [i for i, line in enumerate(basis_lines) if line.startswith('@END')]
    atombases_lines = {el: basis_lines[i + 1:j] for (i, el), j in zip(idxs_atombasis, idxs_end)}

    for el, atombasis_lines in atombases_lines.items():
        element_Z = lut.element_Z_from_sym(el)
        element_data = manip.create_element_data(bs_data, element_Z, 'electron_shells')

        # partition into blocks of shells for this element
        shells_lines = helpers.partition_lines(atombasis_lines, lambda x: shell_begin_re.match(x))

        # gather basis set information
        for sh_lines in shells_lines:
            shell_am, nprim, ncont = helpers.parse_line_regex(shell_begin_re,
                                                              sh_lines[0],
                                                              'shell_am, nprim, ncont',
                                                              convert_int=True)

            # ncont == 1 for VeloxChem
            if ncont != 1:
                raise RuntimeError("Invalid format: number of contracted functions must be 1 for all shells.")

            exponents, coefficients = helpers.parse_primitive_matrix(sh_lines[1:], nprim=nprim, ngen=ncont)

            AM = lut.amchar_to_int(shell_am, hij=True)
            func_type = lut.function_type_from_am(AM, 'gto', 'spherical')

            shell = {
                'function_type': func_type,
                'region': '',
                'angular_momentum': AM,
                'exponents': exponents,
                'coefficients': coefficients
            }

            element_data['electron_shells'].append(shell)

    return bs_data

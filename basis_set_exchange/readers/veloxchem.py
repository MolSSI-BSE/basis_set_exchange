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

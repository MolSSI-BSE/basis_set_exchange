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
Functions for basis set conversion
'''

from .readers import read_formatted_basis_file, read_formatted_basis_str
from .writers import write_formatted_basis_file, write_formatted_basis_str
from .manip import make_general


def convert_formatted_basis_str(basis_in, in_fmt, out_fmt):
    '''Convert a formatted basis set to another format

    Parameters
    ----------
    basis_in : str
        String representing the formatted input basis set input
    in_fmt : str
        The format of the basis set stored in basis_in
    out_fmt : str
        The desired output format

    Returns
    -------
    str
        The basis set as a str with the new format
    '''

    basis_dict = read_formatted_basis_str(basis_in, in_fmt, validate=True, as_component=False)
    return write_formatted_basis_str(basis_dict, out_fmt)


def convert_formatted_basis_file(file_path_in,
                                 file_path_out,
                                 in_fmt=None,
                                 out_fmt=None,
                                 encoding='utf-8-sig',
                                 make_gen=False):
    '''Convert a formatted basis set file to another format

    Parameters
    ----------
    file_path_in : str
        Path to the file to be read
    file_path_out : str
        Path to the file to be written.
    in_fmt : str
        The format of the basis to be read. If None, it is detected from the file name
    out_fmt : str
        The format of the basis to be written. If None, it is detected from the file name
    encoding : str
        The encoding of the input file

    Returns
    -------
    str
        The basis set as a str with the new format
    '''

    basis_dict = read_formatted_basis_file(file_path_in,
                                           basis_fmt=in_fmt,
                                           encoding=encoding,
                                           validate=True,
                                           as_component=False)
    if make_gen:
        basis_dict = make_general(basis_dict, use_copy=False)

    write_formatted_basis_file(basis_dict, file_path_out, basis_fmt=out_fmt)

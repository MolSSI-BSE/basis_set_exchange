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
Completers & validators for argcomplete
'''

import os
from .. import api, writers, readers


def _fix_datadir(data_dir):
    # Handle tilde and variables. These may not have
    # been substituted by the shell at this point
    if data_dir:
        data_dir = os.path.expanduser(data_dir)
        data_dir = os.path.expandvars(data_dir)
    return data_dir


def cli_case_insensitive_validator(s1, s2):
    s1 = s1.lower()
    s2 = s2.lower()
    return s1.startswith(s2)


def cli_bsname_completer(**kwargs):
    # Get the data dir if it has been specified already
    data_dir = _fix_datadir(kwargs['parsed_args'].data_dir)
    return api.get_all_basis_names(data_dir)


def cli_family_completer(**kwargs):
    # Get the data dir if it has been specified already
    data_dir = _fix_datadir(kwargs['parsed_args'].data_dir)
    return api.get_families(data_dir)


def cli_write_fmt_completer(**kwargs):
    return writers.get_writer_formats()


def cli_read_fmt_completer(**kwargs):
    return readers.get_reader_formats()


def cli_reffmt_completer(**kwargs):
    return api.get_reference_formats()


def cli_role_completer(**kwargs):
    return api.get_roles()


def cli_readerfmt_completer(**kwargs):
    return readers.get_reader_formats()

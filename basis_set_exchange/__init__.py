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
Basis Set Exchange Python library

This package contains utilities for obtaining, reading, writing,
and converting basis set information
'''

# Check to make sure we are using python 3
import sys

if sys.version_info < (3, 0):
    raise RuntimeError("This library requires python 3")

# Just import the basic user API
from .api import (get_basis, lookup_basis_by_role, get_metadata, get_reference_data, get_all_basis_names,
                  get_references, get_basis_family, filter_basis_sets, get_families, get_family_notes, get_basis_notes,
                  has_basis_notes, has_family_notes, get_roles, get_formats, version, get_data_dir)

from .readers import read_formatted_basis_file, read_formatted_basis_str, get_reader_formats
from .writers import write_formatted_basis_file, write_formatted_basis_str, get_writer_formats
from .convert import convert_formatted_basis_file, convert_formatted_basis_str
from .refconverters import get_reference_formats
from .validator import validate_file, validate_data

from .bundle import create_bundle, get_archive_types

from importlib.metadata import version
__version__ = version("basis_set_exchange")

def get_version():
    return __version__
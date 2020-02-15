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
                  has_basis_notes, has_family_notes, get_roles, get_formats,
                  version, get_data_dir)

from .readers import read_formatted_basis_file, read_formatted_basis_str, get_reader_formats
from .writers import write_formatted_basis_file, write_formatted_basis_str, get_writer_formats
from .convert import convert_formatted_basis_file, convert_formatted_basis_str
from .refconverters import get_reference_formats
from .validator import validate_file, validate_data

from .bundle import create_bundle, get_archive_types

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions

'''
Basis Set Exchange

Contains utilities for reading, writing, and converting
basis set information
'''

# Just import the basic user API
from .api import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions

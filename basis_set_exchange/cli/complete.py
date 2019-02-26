'''
Completers & validators for argcomplete
'''

import os
from .. import api, curate


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


def cli_fmt_completer(**kwargs):
    return api.get_formats()


def cli_reffmt_completer(**kwargs):
    return api.get_reference_formats()


def cli_role_completer(**kwargs):
    return api.get_roles()


def cli_readerfmt_completer(**kwargs):
    return curate.get_reader_formats()

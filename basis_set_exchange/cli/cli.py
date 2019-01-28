'''
Command line interface for the basis set exchange
'''

import os
import argparse
import argcomplete
from .. import api
from .. import version
from .handlers import *
from .complete import *
from .check import *


def run_bse_cli():
    ################################################################################################
    # NOTE: I am deliberately not using the 'choices' argument in add_argument. I could use it
    # for formats, etc, however I wouldn't want to use it for basis set names. Therefore, I handle
    # all of that manually so that error output is consistent and clean
    ################################################################################################

    ########################################
    # Main global options
    ########################################
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-V', action='version', version='basis_set_exchange ' + version())
    parser.add_argument('-d', '--data-dir', metavar='PATH', help='Override which data directory to use')
    parser.add_argument('-o', '--output', metavar='PATH', help='Output to given file rather than stdout')

    subparsers = parser.add_subparsers(metavar='subcommand', dest='subcmd')
    subparsers.required = True # https://bugs.python.org/issue9253#msg186387

    ########################################
    # Listing of data-independent info
    ########################################
    # list-formats subcommand
    subp = subparsers.add_parser('list-formats', help='Output a list all available basis set formats and descriptions')
    subp.add_argument('-n', '--no-description', action='store_true', help='Print only the format names')

    # list-ref-formats subcommand
    subp = subparsers.add_parser('list-ref-formats', help='Output a list all available reference formats and descriptions')
    subp.add_argument('-n', '--no-description', action='store_true', help='Print only the reference format names')

    # list-roles subcommand
    subp = subparsers.add_parser('list-roles', help='Output a list all available roles and descriptions')
    subp.add_argument('-n', '--no-description', action='store_true', help='Print only the role names')

    ########################################
    # Listing of general info and metadata
    ########################################
    # list-basis-sets subcommand
    subp = subparsers.add_parser('list-basis-sets', help='Output a list all available basis sets and descriptions')
    subp.add_argument('-n', '--no-description', action='store_true', help='Print only the basis set names')
    subp.add_argument('-f', '--family', help='Limit the basis set list to only the specified family').completer = cli_family_completer
    subp.add_argument('-r', '--role', help='Limit the basis set list to only the specified role').completer = cli_role_completer
    subp.add_argument('-s', '--substr', help='Limit the basis set list to only basis sets whose name contains the specified substring')

    # list-families subcommand
    subp = subparsers.add_parser('list-families', help='Output a list all available basis set families')

    # lookup-by-role
    subp = subparsers.add_parser('lookup-by-role', help='Lookup a companion/auxiliary basis by primary basis and role')
    subp.add_argument('basis', help='Name of the primary basis we want the auxiliary basis for').completer = cli_bsname_completer
    subp.add_argument('role', help='Role of the auxiliary basis to look for').completer = cli_role_completer

    #################################
    # Output of info
    #################################
    # get-basis subcommand
    subp = subparsers.add_parser('get-basis', help='Output a formatted basis set')
    subp.add_argument('basis', help='Name of the basis set to output').completer = cli_bsname_completer
    subp.add_argument('fmt', help='Which format to output the basis set as').completer = cli_fmt_completer
    subp.add_argument('--elements', help='Which elements of the basis set to output. Default is all defined in the given basis')
    subp.add_argument('--version', help='Which version of the basis set to output. Default is the latest version')
    subp.add_argument('--noheader', action='store_true', help='Do not output the header at the top')
    subp.add_argument('--unc-gen', action='store_true', help='Remove general contractions')
    subp.add_argument('--unc-spdf', action='store_true', help='Remove combined sp, spd, ... contractions')
    subp.add_argument('--unc-seg', action='store_true', help='Remove general contractions')
    subp.add_argument('--opt-gen', action='store_true', help='Optimize general contractions')
    subp.add_argument('--make-gen', action='store_true', help='Make the basis set as generally-contracted as possible')

    # get-refs subcommand
    subp = subparsers.add_parser('get-refs', help='Output references for a basis set')
    subp.add_argument('basis', help='Name of the basis set to output the references for').completer = cli_bsname_completer
    subp.add_argument('reffmt', help='Which format to output the references as').completer = cli_reffmt_completer
    subp.add_argument('--elements', help='Which elements to output the references for. Default is all defined in the given basis.')
    subp.add_argument('--version', help='Which version of the basis set to get the references for')

    # get-info subcommand
    subp = subparsers.add_parser('get-info', help='Output general info and metadata for a basis set')
    subp.add_argument('basis', help='Name of the basis set to output the info for').completer = cli_bsname_completer

    # get-notes subcommand
    subp = subparsers.add_parser('get-notes', help='Output the notes for a basis set')
    subp.add_argument('basis', help='Name of the basis set to output the notes for').completer = cli_bsname_completer

    # get-family subcommand
    subp = subparsers.add_parser('get-family', help='Output the family of a basis set')
    subp.add_argument('basis', help='Name of the basis set to output the family for').completer = cli_bsname_completer

    # get-versions subcommand
    subp = subparsers.add_parser('get-versions', help='Output a list all available versions of a basis set')
    subp.add_argument('basis', help='Name of the basis set to list the versions of').completer = cli_bsname_completer
    subp.add_argument('-n', '--no-description', action='store_true', help='Print only the version numbers')

    # get-family-notes subcommand
    subp = subparsers.add_parser('get-family-notes', help='Get the notes of a family of basis sets')
    subp.add_argument('family', type=str.lower, help='The basis set family to the get the notes of').completer = cli_family_completer

    #############################
    # DONE WITH SUBCOMMANDS
    #############################

    # setup autocomplete
    argcomplete.autocomplete(parser, validator=cli_case_insensitive_validator)

    # Now parse and handle the args
    args = parser.parse_args()

    # Normalize the arguments. I keep all metavars
    # the same for what they represent
    args_keys = vars(args).keys() # What args we have
    if 'data_dir' in args_keys:
        args.data_dir = check_data_dir(args.data_dir)
    if 'basis' in args:
        args.basis = check_basis(args.basis, args.data_dir)
    if 'fmt' in args_keys:
        args.fmt = check_format(args.fmt)
    if 'reffmt' in args_keys:
        args.reffmt = check_ref_format(args.reffmt)
    if 'role' in args_keys:
        args.role = check_role(args.role)
    if 'family' in args_keys:
        args.family = check_family(args.family, args.data_dir)

    handler_map = {
        'list-formats': cli_list_formats,
        'list-ref-formats': cli_list_ref_formats,
        'list-roles': cli_list_roles,
        'list-basis-sets': cli_list_basis_sets,
        'list-families': cli_list_families,
        'lookup-by-role': cli_lookup_by_role,
        'get-basis': cli_get_basis,
        'get-refs': cli_get_refs,
        'get-info': cli_get_info,
        'get-notes': cli_get_notes,
        'get-family': cli_get_family,
        'get-versions': cli_get_versions,
        'get-family-notes': cli_get_family_notes,
    }

    output = handler_map[args.subcmd](args)

    if args.output:
        with open(args.output, 'w') as outfile:
            outfile.write(output)
    else:
        print(output)

    return 0

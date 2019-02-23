'''
Command line interface for the basis set exchange
'''

import argparse
import argcomplete
from .. import version
from .bsecurate_handlers import bsecurate_cli_handle_subcmd
from .check import cli_check_normalize_args
from .complete import (cli_case_insensitive_validator,
                       cli_family_completer, cli_role_completer, cli_bsname_completer,
                       cli_fmt_completer, cli_reffmt_completer)


def run_bsecurate_cli():
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
    # Listing of general info and metadata
    ########################################
    # elements-in-files
    subp = subparsers.add_parser('elements-in-files', help='For a list of JSON files, output what elements are in each file')
    subp.add_argument('files', nargs='+', help='List of files to inspect')


    #############################
    # DONE WITH SUBCOMMANDS
    #############################

    # setup autocomplete
    argcomplete.autocomplete(parser, validator=cli_case_insensitive_validator)

    # Now parse and handle the args
    args = parser.parse_args()

    # Check and make sure basis sets, roles, etc, are valid
    args = cli_check_normalize_args(args)

    # Actually generate the output
    output = bsecurate_cli_handle_subcmd(args)

    if args.output:
        with open(args.output, 'w') as outfile:
            outfile.write(output)
    else:
        print(output)

    return 0

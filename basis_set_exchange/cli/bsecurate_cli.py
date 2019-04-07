'''
Command line interface for the basis set exchange
'''

import argparse
import argcomplete
from .. import version
from .bsecurate_handlers import bsecurate_cli_handle_subcmd
from .check import cli_check_normalize_args
from .complete import cli_case_insensitive_validator, cli_bsname_completer, cli_readerfmt_completer


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
    # get-reader-formats
    subp = subparsers.add_parser('get-reader-formats', help='A list of file formats that can be read')
    subp.add_argument('-n', '--no-description', action='store_true', help='Print only the format names')

    # elements-in-files
    subp = subparsers.add_parser('elements-in-files', help='For a list of JSON files, output what elements are in each file')
    subp.add_argument('files', nargs='+', help='List of files to inspect')

    # elements-in-files
    subp = subparsers.add_parser('component-file-refs', help='For a list of component JSON files, output what elements/references are in each file')
    subp.add_argument('files', nargs='+', help='List of files to inspect')


    ########################################
    # Printing data
    ########################################
    subp = subparsers.add_parser('print-component-file', help='(Pretty) print the contents of a component file')
    subp.add_argument('file', help='File to print')
    subp.add_argument('--elements', help='Which elements of the basis set to output. Default is all defined in the given basis')


    ########################################
    # Manipulating basis set data
    ########################################
    # make-diff
    subp = subparsers.add_parser('make-diff', help='Find/Store the differences between two groups of files')
    subp.add_argument('-l', '--left', nargs='+', required=True, help='Base JSON files')
    subp.add_argument('-r', '--right', nargs='+', required=True, help='JSON files with data to subtract from the base files')


    ########################################
    # Comparing
    ########################################
    # compare-basis-sets
    subp = subparsers.add_parser('compare-basis-sets', help='Compare two basis sets in the data directory')
    subp.add_argument('basis1', help='First basis set to compare').completer = cli_bsname_completer
    subp.add_argument('basis2', help='Second basis set to compare').completer = cli_bsname_completer
    subp.add_argument('--version1', help='Version of the first basis set to compare with. Default is latest')
    subp.add_argument('--version2', help='Version of the second basis set to compare with. Default is latest')
    subp.add_argument('--uncontract-general', action='store_true', help='Remove general contractions before comparing')

    # compare-basis-files
    subp = subparsers.add_parser('compare-basis-files', help='Compare two formatted basis set files')
    subp.add_argument('file1', help='First basis set file to compare')
    subp.add_argument('file2', help='Second basis set file to compare')
    subp.add_argument('--readfmt1', help='Override the file format of file 1').completer = cli_readerfmt_completer
    subp.add_argument('--readfmt2', help='Override the file format of file 2').completer = cli_readerfmt_completer
    subp.add_argument('--uncontract-general', action='store_true', help='Remove general contractions before comparing')


    ########################################
    # Making graphs
    ########################################
    # view-graph
    subp = subparsers.add_parser('view-graph', help='View a file graph for a basis set')
    subp.add_argument('basis', help='Name of the basis set inspect').completer = cli_bsname_completer
    subp.add_argument('--version', help='Which version of the basis set to inspect. Default is the latest version')

    # make-graph-file
    subp = subparsers.add_parser('make-graph-file', help='Make a dot file (and png file) ofr a basis set file graph')
    subp.add_argument('basis', help='Name of the basis set inspect').completer = cli_bsname_completer
    subp.add_argument('outfile', help='Output DOT file to create')
    subp.add_argument('--render', action='store_true', help='Render the DOT file into a corresponding png file')
    subp.add_argument('--version', help='Which version of the basis set to inspect. Default is the latest version')


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
        with open(args.output, 'w', encoding='utf-8') as outfile:
            outfile.write(output)
    else:
        print(output)

    return 0

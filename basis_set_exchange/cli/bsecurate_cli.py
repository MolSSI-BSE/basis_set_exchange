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
Command line interface for the basis set exchange
'''

import argparse
import argcomplete
from basis_set_exchange import get_version
from basis_set_exchange.cli.bsecurate_handlers import bsecurate_cli_handle_subcmd
from basis_set_exchange.cli.check import cli_check_normalize_args
from basis_set_exchange.cli.complete import cli_case_insensitive_validator, cli_bsname_completer, cli_readerfmt_completer


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
    parser.add_argument('-V', action='version', version='basis_set_exchange ' + get_version())
    parser.add_argument('-d', '--data-dir', metavar='PATH', help='Override which data directory to use')
    parser.add_argument('-o', '--output', metavar='PATH', help='Output to given file rather than stdout',
                        default='-', type=argparse.FileType('w', encoding='utf-8'))

    subparsers = parser.add_subparsers(metavar='subcommand', dest='subcmd')
    subparsers.required = True  # https://bugs.python.org/issue9253#msg186387

    ########################################
    # Listing of general info and metadata
    ########################################
    # elements-in-files
    subp = subparsers.add_parser('elements-in-files',
                                 help='For a list of JSON files, output what elements are in each file')
    subp.add_argument('files', nargs='+', help='List of files to inspect')

    # elements-in-files
    subp = subparsers.add_parser(
        'component-file-refs',
        help='For a list of component JSON files, output what elements/references are in each file')
    subp.add_argument('files', nargs='+', help='List of files to inspect')

    ########################################
    # Updating metadata
    ########################################
    subparsers.add_parser('update-metadata', help='Update the metadata in the repository')

    ########################################
    # Printing data
    ########################################
    subp = subparsers.add_parser('print-component-file', help='(Pretty) print the contents of a component file')
    subp.add_argument('file', help='File to print')
    subp.add_argument('--elements',
                      help='Which elements of the basis set to output. Default is all defined in the given basis')

    ########################################
    # Manipulating basis set data
    ########################################
    # make-diff
    subp = subparsers.add_parser('make-diff', help='Find/Store the differences between two groups of files')
    subp.add_argument('-l', '--left', nargs='+', required=True, help='Base JSON files')
    subp.add_argument('-r',
                      '--right',
                      nargs='+',
                      required=True,
                      help='JSON files with data to subtract from the base files')

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

    # compare-basis-to-file
    subp = subparsers.add_parser('compare-basis-to-file', help='Compare basis set in data directory to file')
    subp.add_argument('basis', help='Basis set to compare')
    subp.add_argument('file', help='Basis set file to compare to')
    subp.add_argument('--readfmt', help='Override the file format').completer = cli_readerfmt_completer
    subp.add_argument('--version', help='Version of the basis set to compare with. Default is latest')
    subp.add_argument('--uncontract-general', action='store_true', help='Remove general contractions before comparing')

    ########################################
    # Making graphs
    ########################################
    # view-graph
    subp = subparsers.add_parser('view-graph', help='View a file graph for a basis set')
    subp.add_argument('basis', help='Name of the basis set inspect').completer = cli_bsname_completer
    subp.add_argument('--version', help='Which version of the basis set to inspect. Default is the latest version')

    # make-graph-file
    subp = subparsers.add_parser('make-graph-file', help='Make a dot file (and png file) for a basis set file graph')
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

    with args.output:
        args.output.write(output + '\n')

    return 0


if __name__ == "__main__":
    run_bsecurate_cli()

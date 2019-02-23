'''
Handlers for command line subcommands
'''

from .. import curate
from ..misc import compact_elements
from .common import format_columns


def _bsecurate_cli_elements_in_files(args):
    '''Handles the elements-in-files subcommand'''
    data = curate.elements_in_files(args.files)
    return '\n'.join(format_columns(data.items()))


def _bsecurate_cli_view_graph(args):
    '''Handles the view-graph subcommand'''

    curate.view_graph(args.basis, args.version, args.data_dir)
    return ''


def _bsecurate_cli_make_graph_file(args):
    '''Handles the make-graph-file subcommand'''

    curate.make_graph_file(args.basis, args.outfile, args.render, args.version, args.data_dir)
    return ''


def bsecurate_cli_handle_subcmd(args):
    handler_map = {
        'elements-in-files': _bsecurate_cli_elements_in_files,
        'view-graph': _bsecurate_cli_view_graph,
        'make-graph-file': _bsecurate_cli_make_graph_file
    }

    return handler_map[args.subcmd](args)

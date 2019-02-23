'''
Handlers for command line subcommands
'''

from .. import curate
from ..misc import compact_elements
from .common import format_columns


def _bsecurate_cli_elements_in_files(args):
    '''Handles the list-basis-sets subcommand'''
    data = curate.elements_in_files(args.files)
    return '\n'.join(format_columns(data.items()))


def bsecurate_cli_handle_subcmd(args):
    handler_map = {
        'elements-in-files': _bsecurate_cli_elements_in_files
    }

    return handler_map[args.subcmd](args)

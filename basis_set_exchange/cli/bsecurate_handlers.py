'''
Handlers for command line subcommands
'''

from .. import curate, printing, fileio
from .common import format_columns


def _bsecurate_cli_get_reader_formats(args):
    '''Handles the get-file-types subcommand'''

    all_formats = curate.get_reader_formats()

    if args.no_description:
        liststr = all_formats.keys()
    else:
        liststr = format_columns(all_formats.items())

    return '\n'.join(liststr)


def _bsecurate_cli_elements_in_files(args):
    '''Handles the elements-in-files subcommand'''
    data = curate.elements_in_files(args.files)
    return '\n'.join(format_columns(data.items()))


def _bsecurate_cli_component_file_refs(args):
    '''Handles the component-file-refs subcommand'''
    data = curate.component_file_refs(args.files)

    s = ''

    for cfile, cdata in data.items():
        s += cfile + '\n'
        rows = []
        for el, refs in cdata:
            rows.append(('    ' + el, ' '.join(refs)))
        s += '\n'.join(format_columns(rows)) + '\n\n'

    return s


def _bsecurate_cli_print_component_file(args):
    '''Handles the print-component-file subcommand'''

    data = fileio.read_json_basis(args.file)
    return printing.component_basis_str(data, elements=args.elements)


def _bsecurate_cli_compare_basis_sets(args):
    '''Handles compare-basis-sets subcommand'''
    ret = curate.compare_basis_sets(args.basis1, args.basis2, args.version1, args.version2, args.uncontract_general,
          args.data_dir, args.data_dir)
    if ret:
        return "No difference found"
    else:
        return "DIFFERENCES FOUND. SEE ABOVE"


def _bsecurate_cli_compare_basis_files(args):
    '''Handles compare-basis-files subcommand'''
    ret = curate.compare_basis_files(args.file1, args.file2, args.readfmt1, args.readfmt2, args.uncontract_general)

    if ret:
        return "No difference found"
    else:
        return "DIFFERENCES FOUND. SEE ABOVE"


def _bsecurate_cli_make_diff(args):
    '''Handles the view-graph subcommand'''

    curate.diff_json_files(args.left, args.right)
    return ''


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
        'get-reader-formats': _bsecurate_cli_get_reader_formats,
        'elements-in-files': _bsecurate_cli_elements_in_files,
        'component-file-refs': _bsecurate_cli_component_file_refs,
        'print-component-file': _bsecurate_cli_print_component_file,
        'compare-basis-sets': _bsecurate_cli_compare_basis_sets,
        'compare-basis-files': _bsecurate_cli_compare_basis_files,
        'make-diff': _bsecurate_cli_make_diff,
        'view-graph': _bsecurate_cli_view_graph,
        'make-graph-file': _bsecurate_cli_make_graph_file
    }

    return handler_map[args.subcmd](args)

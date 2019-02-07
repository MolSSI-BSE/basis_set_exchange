'''
Handlers for command line subcommands
'''

from .. import api
from .. import bundle
from ..misc import compact_elements


def _format_columns(lines, prefix=''):
    '''
    Create a simple column output

    Parameters
    ----------
    lines : list
        List of lines to format. Each line is a tuple/list with each
        element corresponding to a column
    prefix : str
        Characters to insert at the beginning of each line

    Returns
    -------
    str
        Columnated output as one big string
    '''
    if len(lines) == 0:
        return ''

    ncols = 0
    for l in lines:
        ncols = max(ncols, len(l))

    if ncols == 0:
        return ''

    # We only find the max strlen for all but the last col
    maxlen = [0] * (ncols - 1)
    for l in lines:
        for c in range(ncols - 1):
            maxlen[c] = max(maxlen[c], len(l[c]))

    fmtstr = prefix + '  '.join(['{{:{x}}}'.format(x=x) for x in maxlen])
    fmtstr += '  {}'
    return [fmtstr.format(*l) for l in lines]


def _cli_list_basis_sets(args):
    '''Handles the list-basis-sets subcommand'''
    metadata = api.filter_basis_sets(args.substr, args.family, args.role, args.data_dir)

    if args.no_description:
        liststr = metadata.keys()
    else:
        liststr = _format_columns([(k, v['description']) for k, v in metadata.items()])

    return '\n'.join(liststr)


def _cli_list_families(args):
    '''Handles the list-families subcommand'''
    families = api.get_families(args.data_dir)
    return '\n'.join(families)


def _cli_list_formats(args):
    '''Handles the list-formats subcommand'''
    all_formats = api.get_formats()

    if args.no_description:
        liststr = all_formats.keys()
    else:
        liststr = _format_columns(all_formats.items())

    return '\n'.join(liststr)


def _cli_list_ref_formats(args):
    '''Handles the list-ref-formats subcommand'''
    all_refformats = api.get_reference_formats()

    if args.no_description:
        liststr = all_refformats.keys()
    else:
        liststr = _format_columns(all_refformats.items())

    return '\n'.join(liststr)


def _cli_list_roles(args):
    '''Handles the list-roles subcommand'''
    all_roles = api.get_roles()

    if args.no_description:
        liststr = all_roles.keys()
    else:
        liststr = _format_columns(all_roles.items())

    return '\n'.join(liststr)


def _cli_lookup_by_role(args):
    '''Handles the lookup-by-role subcommand'''
    return api.lookup_basis_by_role(args.basis, args.role, args.data_dir)


def _cli_get_basis(args):
    '''Handles the get-basis subcommand'''

    return api.get_basis(
        name=args.basis,
        elements=args.elements,
        version=args.version,
        fmt=args.fmt,
        uncontract_general=args.unc_gen,
        uncontract_spdf=args.unc_spdf,
        uncontract_segmented=args.unc_seg,
        make_general=args.make_gen,
        optimize_general=args.opt_gen,
        data_dir=args.data_dir,
        header=not args.noheader)


def _cli_get_refs(args):
    '''Handles the get-refs subcommand'''
    return api.get_references(
        basis_name=args.basis, elements=args.elements, version=args.version, fmt=args.reffmt, data_dir=args.data_dir)


def _cli_get_info(args):
    '''Handles the get-info subcommand'''

    bs_meta = api.get_metadata(args.data_dir)[args.basis]
    ret = []
    ret.append('-' * 80)
    ret.append(args.basis)
    ret.append('-' * 80)
    ret.append('    Display Name: ' + bs_meta['display_name'])
    ret.append('     Description: ' + bs_meta['description'])
    ret.append('            Role: ' + bs_meta['role'])
    ret.append('          Family: ' + bs_meta['family'])
    ret.append('  Function Types: ' + ','.join(bs_meta['functiontypes']))
    ret.append('  Latest Version: ' + bs_meta['latest_version'])
    ret.append('')

    aux = bs_meta['auxiliaries']
    if len(aux) == 0:
        ret.append('Auxiliary Basis Sets: None')
    else:
        ret.append('Auxiliary Basis Sets:')
        ret.extend(_format_columns(list(aux.items()), '    '))

    ver = bs_meta['versions']
    ret.append('')
    ret.append('Versions:')

    # Print 3 columns - version, elements, revision description
    version_lines = _format_columns([(k, compact_elements(v['elements']), v['revdesc']) for k, v in ver.items()],
                                    '    ')
    ret.extend(version_lines)

    return '\n'.join(ret)


def _cli_get_notes(args):
    '''Handles the get-notes subcommand'''
    return api.get_basis_notes(args.basis, args.data_dir)


def _cli_get_family(args):
    '''Handles the get-family subcommand'''
    return api.get_basis_family(args.basis, args.data_dir)


def _cli_get_versions(args):
    '''Handles the get-versions subcommand'''
    name = args.basis.lower()
    metadata = api.get_metadata(args.data_dir)
    if not name in metadata:
        raise KeyError(
            "Basis set {} does not exist. For a complete list of basis sets, use the 'list-basis-sets' command".format(
                name))

    version_data = {k: v['revdesc'] for k, v in metadata[name]['versions'].items()}

    if args.no_description:
        liststr = version_data.keys()
    else:
        liststr = _format_columns(version_data.items())

    return '\n'.join(liststr)


def _cli_get_family_notes(args):
    '''Handles the get-family-notes subcommand'''
    return api.get_family_notes(args.family, args.data_dir)


def _cli_create_bundle(args):
    '''Handles the create-bundle subcommand'''
    bundle.create_bundle(args.bundle_file, args.fmt, args.reffmt, args.archive_type, args.data_dir)
    return "Created " + args.bundle_file


def cli_handle_bse_subcmd(args):
    handler_map = {
        'list-formats': _cli_list_formats,
        'list-ref-formats': _cli_list_ref_formats,
        'list-roles': _cli_list_roles,
        'list-basis-sets': _cli_list_basis_sets,
        'list-families': _cli_list_families,
        'lookup-by-role': _cli_lookup_by_role,
        'get-basis': _cli_get_basis,
        'get-refs': _cli_get_refs,
        'get-info': _cli_get_info,
        'get-notes': _cli_get_notes,
        'get-family': _cli_get_family,
        'get-versions': _cli_get_versions,
        'get-family-notes': _cli_get_family_notes,
        'create-bundle': _cli_create_bundle
    }

    return handler_map[args.subcmd](args)

'''
Sorting of BSE related dictionaries and data
'''

import sys
import copy

# Dictionaries for python 3.6 and above are insertion ordered
# For other versions, use an OrderedDict
_use_odict = sys.version_info.major == 3 and sys.version_info.minor < 6

if _use_odict:
    from collections import OrderedDict


def sort_basis_dict(bs):
    """Sorts a basis set dictionary into a standard order

    This, for example, allows the written file to be more easily read by humans by,
    for example, putting the name and description before more detailed fields.

    This is generally for cosmetic reasons. However, users will generally like things
    in a consistent order
    """

    # yapf: disable
    _keyorder = [
        # Schema stuff
        'molssi_bse_schema', 'schema_type', 'schema_version',

        # Auxiliary block
         'jkfit', 'jfit', 'rifit', 'admmfit', 'dftxfit', 'dftjfit',

        # Basis set metadata
        'name', 'names', 'aliases', 'flags', 'family', 'description', 'role', 'auxiliaries',
        'notes', 'function_types',

        # Reference stuff
        'reference_description', 'reference_keys',

        # Version metadata
        'version', 'revision_description',

        # Sources of components
        'data_source',

        # Elements and data
        'elements', 'references', 'ecp_electrons',
        'electron_shells', 'ecp_potentials', 'components',

        # Shell information
        'function_type', 'region', 'angular_momentum', 'exponents',
        'coefficients',
        'ecp_type', 'angular_momentum', 'r_exponents', 'gaussian_exponents',
        'coefficients'
    ]
    # yapf: enable

    # Add integers for the elements (being optimistic that element 150 will be found someday)
    _keyorder.extend([str(x) for x in range(150)])

    bs_sorted = sorted(bs.items(), key=lambda x: _keyorder.index(x[0]))
    if _use_odict:
        bs_sorted = OrderedDict(bs_sorted)
    else:
        bs_sorted = dict(bs_sorted)

    for k, v in bs_sorted.items():
        # If this is a dictionary, sort recursively
        # If this is a list, sort each element but DO NOT sort the list itself.
        if isinstance(v, dict):
            bs_sorted[k] = sort_basis_dict(v)
        elif isinstance(v, list):
            # Note - the only nested list is with coeffs, which shouldn't be sorted
            #        (so we don't have to recurse into lists of lists)
            bs_sorted[k] = [sort_basis_dict(x) if isinstance(x, dict) else x for x in v]

    return bs_sorted


def sort_shell(shell, use_copy=True):
    """
    Sort a basis set shell into a standard order

    If use_copy is True, the input shells are not modified.
    """

    if use_copy:
        shell = copy.deepcopy(shell)

    # Transpose of coefficients
    tmp_c = list(map(list, zip(*shell['coefficients'])))

    # For each primitive, find the index of the first nonzero coefficient
    nonzero_idx = [next((i for i, x in enumerate(c) if float(x) != 0.0), None) for c in tmp_c]

    # Zip together exponents and coeffs for sorting
    tmp = zip(shell['exponents'], tmp_c, nonzero_idx)

    # Sort by decreasing value of exponent
    tmp = sorted(tmp, key=lambda x: -float(x[0]))

    # Now (stable) sort by first non-zero coefficient
    tmp = sorted(tmp, key=lambda x: int(x[2]))

    # Unpack, and re-transpose the coefficients
    tmp_c = [x[1] for x in tmp]
    shell['exponents'] = [x[0] for x in tmp]

    # Now sort the columns of the coefficient by index of first nonzero coefficient
    tmp_c = list(map(list, zip(*tmp_c)))
    nonzero_idx = [next((i for i, x in enumerate(c) if float(x) != 0.0), None) for c in tmp_c]

    tmp = zip(tmp_c, nonzero_idx)
    tmp = sorted(tmp, key=lambda x: int(x[1]))
    tmp_c = [x[0] for x in tmp]

    shell['coefficients'] = tmp_c

    return shell


def sort_shells(shells, use_copy=True):
    """
    Sort a list of basis set shells into a standard order

    The order within a shell is by decreasing value of the exponent.

    The order of the shell list is in increasing angular momentum, and then
    by decreasing number of primitives, then decreasing value of the largest exponent.

    If use_copy is True, the input shells are not modified.
    """

    if use_copy:
        shells = copy.deepcopy(shells)

    # Sort primitives within a shell
    # (copying already handled above)
    shells = [sort_shell(sh, False) for sh in shells]

    # Sort the list by increasing AM, then general contraction level, then decreasing highest exponent
    return list(
        sorted(
            shells,
            key=lambda x: (max(x['angular_momentum']), -len(x['exponents']), -len(x['coefficients']), -float(
                max(x['exponents'])))))


def sort_potentials(potentials, use_copy=True):
    """
    Sort a list of ECP potentials into a standard order

    The order within a potential is not modified.

    The order of the shell list is in increasing angular momentum, with the largest
    angular momentum being moved to the front.

    If use_copy is True, the input potentials are not modified.
    """

    if use_copy:
        potentials = copy.deepcopy(potentials)

    # Sort by increasing AM, then move the last element to the front
    potentials = list(sorted(potentials, key=lambda x: x['angular_momentum']))
    potentials.insert(0, potentials.pop())
    return potentials


def sort_basis(basis, use_copy=True):
    """
    Sorts all the information in a basis set into a standard order

    If use_copy is True, the input basis set is not modified.
    """

    if use_copy:
        basis = copy.deepcopy(basis)

    for k, el in basis['elements'].items():
        if 'electron_shells' in el:
            el['electron_shells'] = sort_shells(el['electron_shells'], False)
        if 'ecp_potentials' in el:
            el['ecp_potentials'] = sort_potentials(el['ecp_potentials'], False)

    return sort_basis_dict(basis)


def sort_single_reference(ref_entry):
    """Sorts a dictionary containing data for a single reference into a standard order
    """

    # yapf: disable
    _keyorder = [
        # Schema stuff
        # This function gets called on the schema 'entry', too
        'schema_type', 'schema_version',

        # Type of the entry
        'type',

        # Actual publication info
        'authors', 'title', 'booktitle', 'series', 'editors', 'journal',
        'institution', 'volume', 'number', 'page', 'year', 'note', 'publisher',
        'address', 'isbn', 'doi'
    ]
    # yapf: enable

    sorted_entry = sorted(ref_entry.items(), key=lambda x: _keyorder.index(x[0]))

    if _use_odict:
        return OrderedDict(sorted_entry)
    else:
        return dict(sorted_entry)


def sort_references_dict(refs):
    """Sorts a reference dictionary into a standard order

    The keys of the references are also sorted, and the keys for the data for each
    reference are put in a more canonical order.
    """

    if _use_odict:
        refs_sorted = OrderedDict()
    else:
        refs_sorted = dict()

    # We insert this first, That is ok - it will be overwritten
    # with the sorted version later
    refs_sorted['molssi_bse_schema'] = refs['molssi_bse_schema']

    # This sorts the entries by reference key (author1985a, etc)
    for k, v in sorted(refs.items()):
        refs_sorted[k] = sort_single_reference(v)

    return refs_sorted

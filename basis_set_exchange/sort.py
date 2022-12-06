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
Sorting of BSE related dictionaries and data
'''

import sys
import copy
from .ints import gto_Rsq_contr

# Dictionaries for python 3.6 and above are insertion ordered
# For other versions, use an OrderedDict
_use_odict = sys.version_info.major == 3 and sys.version_info.minor < 6

if _use_odict:
    from collections import OrderedDict


def _spatial_extent(sh):
    """Computes the spatial extent for the orbitals on the shell"""

    rsq = []
    if sh['function_type'][:3] == 'gto':  # Catches GTO, spherical and cartesian
        if len(sh['angular_momentum']) == 1:
            # General contraction
            rsq_mat = gto_Rsq_contr(sh['exponents'], sh['coefficients'], sh['angular_momentum'][0])
            rsq = [rsq_mat[i][i] for i in range(len(rsq_mat))]
        else:
            # SP shell etc
            for iam in range(len(sh['angular_momentum'])):
                rsq_mat = gto_Rsq_contr(sh['exponents'], [sh['coefficients'][iam]], sh['angular_momentum'][iam])
                # We should only have a single element
                assert (len(rsq_mat) == 1 and len(rsq_mat[0]) == 1)
                rsq.append(rsq_mat[0][0])
    else:
        raise RuntimeError('Function type {} not handled'.format(sh['function_type']))

    return rsq


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
        'jkfit', 'jfit', 'rifit', 'optri', 'admmfit', 'dftxfit', 'dftjfit', 'guess',

        # Basis set metadata
        'name', 'names', 'aliases', 'tags', 'family', 'description', 'role', 'auxiliaries',
        'notes', 'function_types',

        # Reference stuff
        'reference_description', 'reference_keys',

        # Version metadata
        'version', 'revision_description', 'revision_date',

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

    tmp_c = shell['coefficients']
    tmp_z = shell['exponents']

    # Exponents should be in decreasing order
    zidx = [x for x, y in sorted(enumerate(tmp_z), key=lambda x: -float(x[1]))]

    if len(shell['angular_momentum']) == 1:
        rsq_vec = _spatial_extent(shell)
        cidx = sorted(range(len(rsq_vec)), key=rsq_vec.__getitem__)
    else:
        # This is an SP shell etc; we only have one contraction per am
        # so we don't have to sort the contractions.
        cidx = range(len(tmp_c))

    # Collect the exponents and coefficients
    newexp = [tmp_z[i] for i in zidx]
    newcoef = [[tmp_c[i][j] for j in zidx] for i in cidx]

    shell['exponents'] = newexp
    shell['coefficients'] = newcoef

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

    # Collect minimum spatial extent of the shells
    min_rms = []
    for sh in shells:
        min_rms.append(min(_spatial_extent(sh)))

    # Zip together to sort
    tmp = zip(shells, min_rms)

    # Sort the list by increasing AM and then by increasing spatial extent
    tmp_sorted = sorted(tmp, key=lambda x: (max(x[0]['angular_momentum']), x[1]))

    return [x[0] for x in tmp_sorted]


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
    potentials = sorted(potentials, key=lambda x: x['angular_momentum'])
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
        '_entry_type', 'type',

        # Actual publication info
        'authors', 'title', 'booktitle', 'series', 'editors', 'journal',
        'institution', 'school', 'volume', 'number', 'pages', 'year', 'note', 'publisher',
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

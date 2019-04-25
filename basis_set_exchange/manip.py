"""
Common basis set manipulations

This module contains functions for uncontracting and merging basis set
data, as well as some other small functions.
"""

import copy


def merge_element_data(dest, sources, use_copy=True):
    """
    Merges the basis set data for an element from multiple sources
    into dest.

    The destination is not modified, and a (shallow) copy of dest is returned
    with the data from sources added.

    If use_copy is True, then the data merged into dest will be a (deep)
    copy of that found in sources. Otherwise, data may be shared between dest
    and sources
    """

    if dest is not None:
        ret = dest.copy()
    else:
        ret = {}

    if use_copy:
        sources = copy.deepcopy(sources)

    # Note that we are not copying notes/data_sources
    for s in sources:
        if 'electron_shells' in s:
            if 'electron_shells' not in ret:
                ret['electron_shells'] = []
            ret['electron_shells'].extend(s['electron_shells'])
        if 'ecp_potentials' in s:
            if 'ecp_potentials' in ret:
                raise RuntimeError('Cannot overwrite existing ECP')
            ret['ecp_potentials'] = s['ecp_potentials']
            ret['ecp_electrons'] = s['ecp_electrons']
        if 'references' in s:
            if 'references' not in ret:
                ret['references'] = []
            for ref in s['references']:
                if not ref in ret['references']:
                    ret['references'].append(ref)

    return ret


def prune_shell(shell, use_copy=True):
    """
    Removes exact duplicates of primitives, and condenses duplicate exponents
    into general contractions

    Also removes primitives if all coefficients are zero
    """

    new_exponents = []
    new_coefficients = []

    exponents = shell['exponents']
    nprim = len(exponents)

    # transpose of the coefficient matrix
    coeff_t = list(map(list, zip(*shell['coefficients'])))

    # Group by exponents
    ex_groups = []
    for i in range(nprim):
        for ex in ex_groups:
            if float(exponents[i]) == float(ex[0]):
                ex[1].append(coeff_t[i])
                break
        else:
            ex_groups.append((exponents[i], [coeff_t[i]]))

    # Now collapse within groups
    for ex in ex_groups:
        if len(ex[1]) == 1:
            # only add if there is a nonzero contraction coefficient
            if not all([float(x) == 0.0 for x in ex[1][0]]):
                new_exponents.append(ex[0])
                new_coefficients.append(ex[1][0])
            continue

        # ex[1] contains rows of coefficients. The length of ex[1]
        # is the number of times the exponent is duplicated. Columns represent general contractions.
        # We want to find the non-zero coefficient in each column, if it exists
        # The result is a single row with a length representing the number
        # of general contractions

        new_coeff_row = []

        # so take yet another transpose.
        ex_coeff = list(map(list, zip(*ex[1])))
        for g in ex_coeff:
            nonzero = [x for x in g if float(x) != 0.0]
            if len(nonzero) > 1:
                raise RuntimeError("Exponent {} is duplicated within a contraction".format(ex[0]))

            if len(nonzero) == 0:
                new_coeff_row.append(g[0])
            else:
                new_coeff_row.append(nonzero[0])

        # only add if there is a nonzero contraction coefficient anywhere for this exponent
        if not all([float(x) == 0.0 for x in new_coeff_row]):
            new_exponents.append(ex[0])
            new_coefficients.append(new_coeff_row)

    # take the transpose again, putting the general contraction
    # as the slowest index
    new_coefficients = list(map(list, zip(*new_coefficients)))

    shell['exponents'] = new_exponents
    shell['coefficients'] = new_coefficients

    return shell


def prune_basis(basis, use_copy=True):
    """
    Removes primitives that have a zero coefficient, and
    removes duplicate primitives and shells

    This only finds EXACT duplicates, and is meant to be used
    after other manipulations

    If use_copy is True, the input basis set is not modified.
    """

    if use_copy:
        basis = copy.deepcopy(basis)

    for k, el in basis['elements'].items():
        if not 'electron_shells' in el:
            continue

        shells = el.pop('electron_shells')
        shells = [prune_shell(sh, False) for sh in shells]

        # Remove any duplicates
        el['electron_shells'] = []

        for sh in shells:
            if sh not in el['electron_shells']:
                el['electron_shells'].append(sh)

    return basis


def uncontract_spdf(basis, max_am=0, use_copy=True):
    """
    Removes sp, spd, spdf, etc, contractions from a basis set

    The general contractions are replaced by uncontracted versions

    Contractions up to max_am will be left in place. For example,
    if max_am = 1, spd will be split into sp and d

    The input basis set is not modified. The returned basis
    may have functions with coefficients of zero and may have duplicate
    shells.

    If use_copy is True, the input basis set is not modified.
    """

    if use_copy:
        basis = copy.deepcopy(basis)

    for k, el in basis['elements'].items():

        if not 'electron_shells' in el:
            continue
        newshells = []

        for sh in el['electron_shells']:

            # am will be a list
            am = sh['angular_momentum']
            coeff = sh['coefficients']

            # if this is an sp, spd,...  orbital
            if len(am) > 1:
                newsh = sh.copy()
                newsh['angular_momentum'] = []
                newsh['coefficients'] = []

                ngen = len(sh['coefficients'])
                for g in range(ngen):
                    if am[g] > max_am:
                        newsh2 = sh.copy()
                        newsh2['angular_momentum'] = [am[g]]
                        newsh2['coefficients'] = [coeff[g]]
                        newshells.append(newsh2)
                    else:
                        newsh['angular_momentum'].append(am[g])
                        newsh['coefficients'].append(coeff[g])

                newshells.insert(0, newsh)

            else:
                newshells.append(sh)

        el['electron_shells'] = newshells

    return basis


def uncontract_general(basis, use_copy=True):
    """
    Removes the general contractions from a basis set

    The input basis set is not modified. The returned basis
    may have functions with coefficients of zero and may have duplicate
    shells.

    If use_copy is True, the input basis set is not modified.
    """

    if use_copy:
        basis = copy.deepcopy(basis)

    for k, el in basis['elements'].items():

        if not 'electron_shells' in el:
            continue

        newshells = []

        for sh in el['electron_shells']:
            # See if we actually have to uncontract
            # Also, don't uncontract sp, spd,.... orbitals
            #      (leave that to uncontract_spdf)
            if len(sh['coefficients']) == 1 or len(sh['angular_momentum']) > 1:
                newshells.append(sh)
            else:
                if len(sh['angular_momentum']) == 1:
                    for c in sh['coefficients']:
                        # copy, them replace 'coefficients'
                        newsh = sh.copy()
                        newsh['coefficients'] = [c]
                        newshells.append(newsh)

        el['electron_shells'] = newshells

    # If use_basis is True, we already made our deep copy
    return prune_basis(basis, False)


def uncontract_segmented(basis, use_copy=True):
    """
    Removes the segmented contractions from a basis set

    This implicitly removes general contractions as well,
    but will leave sp, spd, ... orbitals alone

    The input basis set is not modified. The returned basis
    may have functions with coefficients of zero and may have duplicate
    shells.

    If use_copy is True, the input basis set is not modified.
    """

    if use_copy:
        basis = copy.deepcopy(basis)

    for k, el in basis['elements'].items():

        if not 'electron_shells' in el:
            continue

        newshells = []

        for sh in el['electron_shells']:
            exponents = sh['exponents']
            nam = len(sh['angular_momentum'])

            for i in range(len(exponents)):
                newsh = sh.copy()
                newsh['exponents'] = [exponents[i]]
                newsh['coefficients'] = [["1.00000000"] * nam]

                # Remember to transpose the coefficients
                newsh['coefficients'] = list(map(list, zip(*newsh['coefficients'])))

                newshells.append(newsh)

        el['electron_shells'] = newshells

    return basis


def make_general(basis, use_copy=True):
    """
    Makes one large general contraction for each angular momentum

    If use_copy is True, the input basis set is not modified.

    The output of this function is not pretty. If you want to make it nicer,
    use sort_basis afterwards.
    """

    zero = '0.00000000'

    basis = uncontract_spdf(basis, 0, use_copy)

    for k, el in basis['elements'].items():
        if not 'electron_shells' in el:
            continue

        # See what we have
        all_am = []
        for sh in el['electron_shells']:
            if not sh['angular_momentum'] in all_am:
                all_am.append(sh['angular_momentum'])

        all_am = sorted(all_am)

        newshells = []
        for am in all_am:
            newsh = {
                'angular_momentum': am,
                'exponents': [],
                'coefficients': [],
                'region': '',
                'function_type': None,
            }

            # Do exponents first
            for sh in el['electron_shells']:
                if sh['angular_momentum'] != am:
                    continue
                newsh['exponents'].extend(sh['exponents'])

            # Number of primitives in the new shell
            nprim = len(newsh['exponents'])

            cur_prim = 0
            for sh in el['electron_shells']:
                if sh['angular_momentum'] != am:
                    continue

                if newsh['function_type'] is None:
                    newsh['function_type'] = sh['function_type']

                # Make sure the shells we are merging have the same function types
                ft1 = newsh['function_type']
                ft2 = sh['function_type']

                # Check if one function type is the subset of another
                # (should handle gto/gto_spherical, etc)
                if ft1 not in ft2 and ft2 not in ft1:
                    raise RuntimeError("Cannot make general contraction of different function types")

                ngen = len(sh['coefficients'])

                for g in range(ngen):
                    coef = [zero] * cur_prim
                    coef.extend(sh['coefficients'][g])
                    coef.extend([zero] * (nprim - len(coef)))
                    newsh['coefficients'].append(coef)

                cur_prim += len(sh['exponents'])

            newshells.append(newsh)

        el['electron_shells'] = newshells

    return basis


def _is_single_column(col):
    return sum(float(x) != 0.0 for x in col) == 1


def _is_zero_column(col):
    return sum(float(x) != 0.0 for x in col) == 0


def _nonzero_range(vec):
    for idx, x in enumerate(vec):
        if float(x) != 0.0:
            first = idx
            break

    for idx, x in enumerate(reversed(vec)):
        if float(x) != 0.0:
            last = (len(vec) - idx)
            break

    if first is None:
        return (None, None)
    else:
        return (first, last)


def _find_block(mat):

    # Initial range of rows
    row_range = _nonzero_range(mat[0])
    rows = range(row_range[0], row_range[1])

    # Find the right-most column with a nonzero in it
    col_range = (0, 0)
    for r in rows:
        x, y = _nonzero_range([col[r] for col in mat])
        col_range = (min(col_range[0], x), max(col_range[1], y))

    cols = range(col_range[0], col_range[1])

    # Columns may be jagged also
    # Iterate until we don't see any change
    while True:
        row_range_old = row_range
        col_range_old = col_range
        for c in cols:
            x, y = _nonzero_range(mat[c])
            row_range = (min(row_range[0], x), max(row_range[1], y))

        rows = range(row_range[0], row_range[1])

        for r in rows:
            x, y = _nonzero_range([col[r] for col in mat])
            col_range = (min(col_range[0], x), max(col_range[1], y))

        cols = range(col_range[0], col_range[1])

        if col_range == col_range_old and row_range == row_range_old:
            break

    return (rows, cols)


def optimize_general(basis, use_copy=True):
    """
    Optimizes the general contraction using the method of Hashimoto et al

    .. seealso :: | T. Hashimoto, K. Hirao, H. Tatewaki
                  | 'Comment on Dunning's correlation-consistent basis set'
                  | Chemical Physics Letters v243, Issues 1-2, pp, 190-192 (1995)
                  | https://doi.org/10.1016/0009-2614(95)00807-G

    """

    if use_copy:
        basis = copy.deepcopy(basis)

    for k, el in basis['elements'].items():

        if not 'electron_shells' in el:
            continue

        elshells = el.pop('electron_shells')
        el['electron_shells'] = []
        for sh in elshells:
            exponents = sh['exponents']
            coefficients = sh['coefficients']
            nprim = len(exponents)
            nam = len(sh['angular_momentum'])

            if nam > 1 or len(coefficients) < 2:
                el['electron_shells'].append(sh)
                continue

            # First, find columns (general contractions) with a single non-zero value
            single_columns = [idx for idx, c in enumerate(coefficients) if _is_single_column(c)]

            # Find the corresponding rows that have a value in one of these columns
            # Note that at this stage, the row may have coefficients in more than one
            # column. That is ok, we are going to split it off anyway
            single_rows = []
            for col_idx in single_columns:
                col = coefficients[col_idx]
                for row_idx in range(nprim):
                    if float(col[row_idx]) != 0.0:
                        single_rows.append(row_idx)

            # Split those out into new shells, and remove them from the
            # original shell
            new_shells_single = []
            for row_idx in single_rows:
                newsh = copy.deepcopy(sh)
                newsh['exponents'] = [exponents[row_idx]]
                newsh['coefficients'] = [['1.00000000000']]
                new_shells_single.append(newsh)

            exponents = [x for idx, x in enumerate(exponents) if idx not in single_rows]
            coefficients = [x for idx, x in enumerate(coefficients) if idx not in single_columns]
            coefficients = [[x for idx, x in enumerate(col) if not idx in single_rows] for col in coefficients]

            # Remove Zero columns
            #coefficients = [ x for x in coefficients if not _is_zero_column(x) ]

            # Find contiguous rectanglar blocks
            new_shells = []
            while len(exponents) > 0:
                block_rows, block_cols = _find_block(coefficients)

                # add as a new shell
                newsh = copy.deepcopy(sh)
                newsh['exponents'] = [exponents[i] for i in block_rows]
                newsh['coefficients'] = [[coefficients[colidx][i] for i in block_rows] for colidx in block_cols]
                new_shells.append(newsh)

                # Remove from the original exponent/coefficient set
                exponents = [x for idx, x in enumerate(exponents) if idx not in block_rows]
                coefficients = [x for idx, x in enumerate(coefficients) if idx not in block_cols]
                coefficients = [[x for idx, x in enumerate(col) if not idx in block_rows] for col in coefficients]

            # I do this order to mimic the output of the original BSE
            el['electron_shells'].extend(new_shells)
            el['electron_shells'].extend(new_shells_single)

        # Fix coefficients for completely uncontracted shells to 1.0
        for sh in el['electron_shells']:
            if len(sh['coefficients']) == 1 and len(sh['coefficients'][0]) == 1:
                sh['coefficients'][0][0] = '1.0000000'

    return basis

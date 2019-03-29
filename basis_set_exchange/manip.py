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


def prune_basis(basis, use_copy=True):
    """
    Removes primitives that have a zero coefficient, and
    removes duplicate shells

    This only finds EXACT duplicates, and is meant to be used
    after uncontracting

    If use_copy is True, the input basis set is not modified.
    """

    if use_copy:
        basis = copy.deepcopy(basis)

    for k, el in basis['elements'].items():
        if not 'electron_shells' in el:
            continue

        for sh in el['electron_shells']:
            new_exponents = []
            new_coefficients = []

            exponents = sh['exponents']

            # transpose of the coefficient matrix
            coeff_t = list(map(list, zip(*sh['coefficients'])))

            # only add if there is a nonzero contraction coefficient
            for i in range(len(sh['exponents'])):
                if not all([float(x) == 0.0 for x in coeff_t[i]]):
                    new_exponents.append(exponents[i])
                    new_coefficients.append(coeff_t[i])

            # take the transpose again, putting the general contraction
            # as the slowest index
            new_coefficients = list(map(list, zip(*new_coefficients)))

            sh['exponents'] = new_exponents
            sh['coefficients'] = new_coefficients

        # Remove any duplicates
        shells = el.pop('electron_shells')
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

    If split_spdf is True, sp... orbitals will be split apary

    If use_copy is True, the input basis set is not modified.
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
                'harmonic_type': None,
                'function_type': None,
            }

            # Do exponents first
            # Get all unique exponents
            exponents = []

            for sh in el['electron_shells']:
                if sh['angular_momentum'] != am:
                    continue
                exponents.extend(sh['exponents'])

            # Remove duplicates (by checking the float value)
            done_exponents = []
            unique_exponents = []
            for ex in exponents:
                fex = float(ex)
                if not fex in done_exponents:
                    done_exponents.append(fex)
                    unique_exponents.append(ex)

            newsh['exponents'] = unique_exponents

            for sh in el['electron_shells']:
                if sh['angular_momentum'] != am:
                    continue

                if newsh['harmonic_type'] is None:
                    newsh['harmonic_type'] = sh['harmonic_type']
                if newsh['function_type'] is None:
                    newsh['function_type'] = sh['function_type']

                # Make sure the shells we are merging have the same harmonic types and function types
                if newsh['harmonic_type'] != sh['harmonic_type']:
                    raise RuntimeError("Cannot make general contraction of different harmonic types")
                if newsh['function_type'] != sh['function_type']:
                    raise RuntimeError("Cannot make general contraction of different harmonic types")

                ngen = len(sh['coefficients'])

                # Every general contraction shell should add a column to the coefficients
                coeffs = []
                for g in range(ngen):
                    coeff_row = []
                    for ex1 in unique_exponents:
                        fex1 = float(ex1)
                        for idx, ex2 in enumerate(sh['exponents']):
                            fex2 = float(ex2)
                            if fex1 == fex2:
                                coeff_row.append(sh['coefficients'][g][idx])
                                break
                        else:
                            coeff_row.append(zero)

                    coeffs.append(coeff_row)

                newsh['coefficients'].extend(coeffs)

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

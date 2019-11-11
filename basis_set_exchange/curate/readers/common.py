'''
Some helper functions for parsing basis set files
'''


def partition_line_list(lines, condition, start=0):
    all_blocks = []
    cur_block = []

    i = start
    while i < len(lines):
        line = lines[i]
        if condition(line):
            # This is beginning of a new block. If we have anything,
            # append it to block list
            if cur_block:
                all_blocks.append(cur_block)
                cur_block = []

            cur_block.append(line)

        else:
            cur_block.append(line)

        i += 1

    # Handle the last block, if needed
    if cur_block:
        all_blocks.append(cur_block)

    return all_blocks


def parse_primitive_matrix(lines, nprim=None, ngen=None):
    exponents = []
    coefficients = []
    for l in lines:
        l = l.replace('D', 'E')
        l = l.replace('d', 'E')
        s = l.split()
        exponents.append(s[0])
        coefficients.append(s[1:])

    # We need to transpose the coefficient matrix
    # (we store a matrix with primitives being the column index and
    # general contraction being the row index)
    coefficients = list(map(list, zip(*coefficients)))

    # Make sure all coefficients have the same number of coefficients
    for c in coefficients:
        if len(c) != len(coefficients[0]):
            raise RuntimeError("Inconsistent number of primitives in coefficients: {} vs {}".format(
                len(c), len(coefficients[0])))

    # if nprim and/or ngen are given, sanity check
    if nprim is not None:
        nprim = int(nprim)
        if len(exponents) != nprim:
            raise RuntimeError("Inconsistent number of primitives in exponents: {} vs {}".format(
                nprim, len(exponents)))

        # We already checked that all coefficients have the same number of primitives
        # so just check the first general contraction
        if len(coefficients[0]) != nprim:
            raise RuntimeError("Inconsistent number of primitives in coefficients: {} vs {}".format(
                nprim, len(coefficients[0])))

    if ngen is not None:
        ngen = int(ngen)
        if len(coefficients) != ngen:
            raise RuntimeError("Inconsistent number of general contractions: {} vs {}".format(ngen, len(coefficients)))

    return exponents, coefficients


def prune_lines(lines, skipchars='', prune_blank=True):
    lines = [l.strip() for l in lines]

    if skipchars:
        lines = [l for l in lines if len(l) == 0 or l[0] not in skipchars]
    if prune_blank:
        lines = [l for l in lines if l]

    return lines

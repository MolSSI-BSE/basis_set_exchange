'''
Helper functions for writing out basis set in various formats
'''


def _find_point(x):
    if isinstance(x, int):
        return 0
    else:
        return x.index('.')


def _determine_leftpad(column, point_place):
    '''Find how many spaces to put before a column of numbers
       so that all the decimal points line up

    This function takes a column of decimal numbers, and returns a
    vector containing the number of spaces to place before each number
    so that (when possible) the decimal points line up.


    Parameters
    ----------
    column : list
        Numbers that will be printed as a column
    point_place : int
        Number of the character column to put the decimal point
    '''

    # Find the number of digits before the decimal
    ndigits_left = [_find_point(x) for x in column]

    # find the padding per entry, filtering negative numbers
    return [max((point_place - 1) - x, 0) for x in ndigits_left]


def write_matrix(mat, point_place, convert_exp=False):

    # Padding for the whole matrix
    pad = [_determine_leftpad(c, point_place[i]) for i, c in enumerate(mat)]

    # Use the transposes (easier to write out by row)
    pad = list(map(list, zip(*pad)))
    mat = list(map(list, zip(*mat)))

    lines = ''
    for r, row in enumerate(mat):
        line = ''
        for c, val in enumerate(row):
            sp = pad[r][c] - len(line)
            # ensure at least one space
            sp = max(sp, 1)
            line += ' ' * sp + str(mat[r][c])
        lines += line + '\n'

    if convert_exp is True:
        lines = lines.replace('e', 'D')
        lines = lines.replace('E', 'D')

    return lines

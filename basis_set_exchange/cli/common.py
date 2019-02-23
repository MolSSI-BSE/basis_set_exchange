'''
Some common formatting functions, etc
'''

def format_columns(lines, prefix=''):
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



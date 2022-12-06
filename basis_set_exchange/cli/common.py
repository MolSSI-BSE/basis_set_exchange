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
    if not lines:
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

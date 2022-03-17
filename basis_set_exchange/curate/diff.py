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
Computes the difference between basis sets and files
'''

import copy
from .compare import compare_electron_shells
from .. import fileio


def subtract_electron_shells(s1, s2, rel_tol=0.0):
    """
    Returns the difference between two lists of electron shells (s1 - s2)

    This will remove any shells from s1 that are also in s2, within a tolerance
    """

    diff_shells = []
    for sh1 in s1:
        for sh2 in s2:
            if compare_electron_shells(sh1, sh2, rel_tol=rel_tol):
                break
        else:
            diff_shells.append(copy.deepcopy(sh1))

    return diff_shells


def diff_basis_dict(left_list, right_list):
    '''
    Compute the difference between two sets of basis set dictionaries

    The result is a list of dictionaries that correspond to each dictionary in
    `left_list`. Each resulting dictionary will contain only the elements/shells
    that exist in that entry and not in any of the dictionaries in `right_list`.

    This only works on the shell level, and will only subtract entire shells
    that are identical. ECP potentials are not affected.

    The return value contains deep copies of the input data

    Parameters
    ----------
    left_list : list of dict
        Dictionaries to use as the base
    right_list : list of dict
        Dictionaries of basis data to subtract from each dictionary of `left_list`

    Returns
    ----------
    list
        Each object in `left_list` containing data that does not appear in `right_list`
    '''

    ret = []
    for bs1 in left_list:
        res = copy.deepcopy(bs1)
        for bs2 in right_list:
            for el in res['elements'].keys():
                if el not in bs2['elements']:
                    continue  # Element only exist in left

                eldata1 = res['elements'][el]
                eldata2 = bs2['elements'][el]

                s1 = eldata1['electron_shells']
                s2 = eldata2['electron_shells']
                eldata1['electron_shells'] = subtract_electron_shells(s1, s2)

        # Remove any empty elements
        res['elements'] = {k: v for k, v in res['elements'].items() if v['electron_shells']}
        ret.append(res)

    return ret


def diff_json_files(left_files, right_files):
    '''
    Compute the difference between two sets of basis set JSON files

    The output is a set of files that correspond to each file in
    `left_files`. Each resulting dictionary will contain only the elements/shells
    that exist in that entry and not in any of the files in `right_files`.

    This only works on the shell level, and will only subtract entire shells
    that are identical. ECP potentials are not affected.

    `left_files` and `right_files` are lists of file paths. The output
    is written to files with the same names as those in `left_files`,
    but with `.diff` added to the end. If those files exist, they are overwritten.

    Parameters
    ----------
    left_files : list of str
        Paths to JSON files to use as the base
    right_files : list of str
        Paths to JSON files to subtract from each file of `left_files`

    Returns
    ----------
    None
    '''

    left_data = [fileio.read_json_basis(x) for x in left_files]
    right_data = [fileio.read_json_basis(x) for x in right_files]
    d = diff_basis_dict(left_data, right_data)

    for idx, diff_bs in enumerate(d):
        fpath = left_files[idx]
        fileio.write_json_basis(fpath + '.diff', diff_bs)

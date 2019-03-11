'''
Computing the difference between basis sets and files
'''

import copy
from .. import fileio
from .compare import subtract_electron_shells


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
                if not el in bs2['elements']:
                    continue  # Element only exist in left

                eldata1 = res['elements'][el]
                eldata2 = bs2['elements'][el]

                s1 = eldata1['electron_shells']
                s2 = eldata2['electron_shells']
                eldata1['electron_shells'] = subtract_electron_shells(s1, s2)

        # Remove any empty elements
        res['elements'] = {k: v for k, v in res['elements'].items() if len(v['electron_shells']) > 0}
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

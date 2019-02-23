'''
Miscellaneous curation functions
'''

from .. import fileio
from .. import misc


def elements_in_files(filelist):
    '''Get a list of what elements exist in JSON files

    This works on table, element, and component data files

    Parameters
    ----------
    filelist : list
        A list of paths to json files

    Returns
    -------
    dict
        Keys are the file path, value is a compacted element string of
        what elements are in that file 
    '''

    ret = {}
    for fpath in filelist:
        filedata = fileio.read_json_basis(fpath)
        els = list(filedata['basis_set_elements'].keys())
        ret[fpath] = misc.compact_elements(els)

    return ret

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
        els = list(filedata['elements'].keys())
        ret[fpath] = misc.compact_elements(els)

    return ret


def component_file_refs(filelist):
    '''Get a list of what elements/refrences exist in component JSON files

    Parameters
    ----------
    filelist : list
        A list of paths to json files

    Returns
    -------
    dict
        Keys are the file path, value is a list of tuples (compacted element string, refs tuple)
    '''

    ret = {}
    for fpath in filelist:
        filedata = fileio.read_json_basis(fpath)

        refdict = {}
        for el, eldata in filedata['elements'].items():
            refs = tuple(eldata['references'])
            if not refs in refdict:
                refdict[refs] = [el]
            else:
                refdict[refs].append(el)

        entry = []
        for k, v in refdict.items():
            entry.append((misc.compact_elements(v), k))

        ret[fpath] = entry

    return ret

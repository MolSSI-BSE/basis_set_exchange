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
    '''Get a list of what elements/references exist in component JSON files

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
            if refs not in refdict:
                refdict[refs] = [el]
            else:
                refdict[refs].append(el)

        entry = []
        for k, v in refdict.items():
            entry.append((misc.compact_elements(v), k))

        ret[fpath] = entry

    return ret

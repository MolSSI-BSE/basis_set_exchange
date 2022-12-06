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
Converts basis set data to a specified output format
'''

import textwrap
import json

from .. import sort, misc
from .common import get_library_citation
from .bib import write_bib
from .ris import write_ris
from .endnote import write_endnote

# For plain text
from ..references import reference_text

_converter_map = {
    'txt': {
        'display': 'Plain Text',
        'extension': '.txt',
        'comment': '',
        'function': reference_text
    },
    'bib': {
        'display': 'BibTeX',
        'extension': '.bib',
        'comment': '%',
        'function': write_bib
    },
    'ris': {
        'display': 'RIS',
        'extension': '.RIS',
        'comment': '#',
        'function': write_ris
    },
    'endnote': {
        'display': 'EndNote',
        'extension': '.enw',
        'comment': '#',
        'function': write_endnote
    },
    'json': {
        'display': 'JSON',
        'extension': '.json',
        'comment': '',
        'function': None  # Handled separately
    }
}


def convert_references(ref_data, fmt):
    '''
    Returns the basis set references as a string representing
    the data in the specified output format
    '''

    # Make fmt case insensitive
    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown reference format "{}"'.format(fmt))

    # Shortcut for JSON
    if fmt == 'json':
        return json.dumps(ref_data, indent=4, ensure_ascii=False)

    # Sort the data for all references
    for elref in ref_data:
        for rinfo in elref['reference_info']:
            rdata = rinfo['reference_data']
            rinfo['reference_data'] = [(k, sort.sort_single_reference(v)) for k, v in rdata]

    # This function is used to convert a single ref
    single_ref_func = _converter_map[fmt]['function']

    # Comment style
    comment = _converter_map[fmt]['comment']
    comment_line = comment * 80 + '\n'

    # Actually do the conversion
    ref_str = ''

    # First, convert the library citations (for citing the BSE)
    lib_citation_desc, lib_citations = get_library_citation()

    ref_str += comment_line
    ref_str += textwrap.indent(lib_citation_desc, comment + ' ')
    ref_str += comment_line

    for k, r in lib_citations.items():
        ref_str += single_ref_func(k, r) + '\n\n'

    ref_str += comment_line
    ref_str += comment + " References for the basis set\n"
    ref_str += comment_line

    # First, write out the element, description -> key mapping
    # Also make a dict of unique reference to output
    unique_refs = {}

    for ref in ref_data:
        ref_str += comment + ' {}\n'.format(misc.compact_elements(ref['elements']))

        for ri in ref['reference_info']:
            ref_str += comment + '     {}\n'.format(ri['reference_description'])

            single_ref_data = ri['reference_data']

            if len(single_ref_data) == 0:
                ref_str += comment + '         (...no reference...)\n' + comment + '\n'
            else:
                rkeys = [x[0] for x in ri['reference_data']]
                ref_str += comment + '         {}\n{}\n'.format(' '.join(rkeys), comment)

            for k, r in single_ref_data:
                unique_refs[k] = r

    ref_str += '\n\n'

    # Go through them sorted alphabetically by key
    for k, r in sorted(unique_refs.items(), key=lambda x: x[0]):
        ref_str += '{}\n\n'.format(single_ref_func(k, r))

    return ref_str


def get_reference_formats():
    '''Return information about the reference/citation formats available

    The returned data is a map of format to display name. The format
    can be passed as the fmt argument to :func:`get_references`
    '''

    return {k: v['display'] for k, v in _converter_map.items()}


def get_format_extension(fmt):
    '''
    Returns the recommended extension for a given format
    '''

    if fmt is None:
        return 'dict'

    fmt = fmt.lower()
    if fmt not in _converter_map:
        raise RuntimeError('Unknown basis set format "{}"'.format(fmt))

    return _converter_map[fmt]['extension']

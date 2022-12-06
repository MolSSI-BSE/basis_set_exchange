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
Conversion of references to EndNote (.enw) format
'''


def write_endnote(key, ref):
    '''Convert a single reference to endnote format
    '''
    s = ''

    s += '#{} {}\n'.format(ref['_entry_type'], key)
    if ref['_entry_type'] == 'article':
        s += "%0 Journal Article \n"
    elif ref['_entry_type'] == 'misc':
        s += "%0 Generic \n"
    elif ref['_entry_type'] == 'unpublished':
        s += "%0 Unpublished \n"
    elif ref['_entry_type'] == 'incollection':
        s += "%0 Book \n"
    elif ref['_entry_type'] == 'phdthesis':
        s += "%0 Thesis \n"
    elif ref['_entry_type'] == 'techreport':
        s += "%0 Report \n"
    else:
        s += "%0 Generic\n"

    entry_lines = []
    for k, v in ref.items():
        if k == '_entry_type':
            continue

        # Handle authors/editors
        if k == 'authors':
            for author in v:
                entry_lines.append('%A {}'.format(author))
        elif k == 'year':
            entry_lines.append('%D {}'.format(v))
        elif k == 'journal':
            entry_lines.append('%J {}'.format(v))
        elif k == 'volume':
            entry_lines.append('%V {}'.format(v))
        elif k == 'pages':
            entry_lines.append('%P {}'.format(v))
        elif k == 'title':
            entry_lines.append('%T {}'.format(v))
        elif k == 'doi':
            entry_lines.append('%R {}'.format(v))
        else:
            entry_lines.append('%Z {}:{}'.format(k, v))

    s += '\n'.join(entry_lines)
    s += '\n'

    return s

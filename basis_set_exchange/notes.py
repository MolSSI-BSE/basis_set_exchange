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
Functionality for handling basis set and family notes
'''

from . import references


def process_notes(notes, ref_data):
    '''Add reference information to the bottom of a notes file

    `:ref:` tags are removed and the actual reference data is appended
    '''

    ref_keys = ref_data.keys()

    found_refs = set()
    for k in ref_keys:
        if k in notes:
            found_refs.add(k)

    # The block to append
    reference_sec = '\n\n'
    reference_sec += '-------------------------------------------------\n'
    reference_sec += ' REFERENCES MENTIONED ABOVE\n'
    reference_sec += ' (not necessarily references for the basis sets)\n'
    reference_sec += '-------------------------------------------------\n'

    # Add reference data
    if not found_refs:
        return notes

    for r in sorted(found_refs):
        rtxt = references.reference_text(r, ref_data[r])
        reference_sec += rtxt + '\n\n'

    return notes + reference_sec

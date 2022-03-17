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
Test for duplicate data in a basis set
'''

import os
import pytest
import basis_set_exchange as bse
from basis_set_exchange import readers
from .common_testvars import bs_names_vers, curate_test_data_dir


def _test_duplicates(bs_dict, expected):
    '''
    Test for any duplicate data in a basis set
    '''

    found_dupe = False
    for el, eldata in bs_dict['elements'].items():
        if 'electron_shells' in eldata:
            # Quick and dirty
            shells = eldata['electron_shells']

            for sh in shells:
                if shells.count(sh) != 1:
                    print("Shell Dupe: element {}".format(el))
                    found_dupe = True
                    break

        if 'ecp_potentials' in eldata:
            pots = eldata['ecp_potentials']

            for pot in pots:
                if pots.count(pot) != 1:
                    print("ECP Dupe: element {}".format(el))
                    found_dupe = True
                    break

    assert found_dupe == expected


@pytest.mark.parametrize('bs_name,bs_ver', bs_names_vers)
def test_duplicate_data(bs_name, bs_ver):
    '''
    Test for any duplicate data in a basis set
    '''

    bs_dict = bse.get_basis(bs_name, version=bs_ver)
    _test_duplicates(bs_dict, False)


@pytest.mark.parametrize('filename', ['6-31g-bse-DUPE.nw.bz2', 'def2-ecp-DUPE.nw.bz2'])
def test_duplicate_fail(filename):
    filepath = os.path.join(curate_test_data_dir, filename)
    filedata = readers.read_formatted_basis_file(filepath, 'nwchem')
    _test_duplicates(filedata, True)

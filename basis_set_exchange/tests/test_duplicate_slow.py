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

import pytest
import basis_set_exchange as bse
from .common_testvars import bs_names_vers, true_false
from .test_duplicate import _test_duplicates


@pytest.mark.slow
@pytest.mark.parametrize('bs_name,bs_ver', bs_names_vers)
@pytest.mark.parametrize('unc_gen', true_false)
@pytest.mark.parametrize('unc_seg', true_false)
@pytest.mark.parametrize('unc_spdf', true_false)
@pytest.mark.parametrize('make_gen', true_false)
@pytest.mark.parametrize('opt_gen', true_false)
def test_duplicate_slow(bs_name, bs_ver, unc_gen, unc_seg, unc_spdf, opt_gen, make_gen):
    '''
    Test for any duplicate data in a basis set
    '''

    bs_dict = bse.get_basis(bs_name,
                            version=bs_ver,
                            uncontract_general=unc_gen,
                            uncontract_segmented=unc_seg,
                            uncontract_spdf=unc_spdf,
                            make_general=make_gen,
                            optimize_general=opt_gen)

    _test_duplicates(bs_dict, False)

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

"""
Tests BSE curation functions
"""

import os

from basis_set_exchange import curate, api, validator, misc, fileio
from .common_testvars import auth_data_dir

# yapf: disable
# Mapping of filename to refs
_source_data = {'cc-pvdz.1.gbasis.bz2': None,
                'def2-tzvp.1.tm.bz2': 'myref',
                'aug-pcj-1.1.gbs.bz2': ['ref1', 'ref2'],
                'def2-ecp.1.tm.bz2': {'rb': 'ref1', 47: 'ref2', '48': 'ref3', '49-xe': 'ref4'}
}

_expected_files = {'test_subdir/test_aug-pcj-1.1.json':          'H-Ar',
                   'test_subdir/test_cc-pvdz.1.json':            'H-Ar,Ca-Kr',
                   'test_subdir/test_def2-ecp.1.json':           'Rb-Rn',
                   'test_subdir/test_def2-tzvp.1.json':          'H-Rn',
                   'test_subdir/test_def2-tzvp.1.element.json':  'H-Rn',
                   'test_subdir/test_aug-pcj-1.1.element.json':  'H-Ar',
                   'test_subdir/test_def2-ecp.1.element.json':   'Rb-Rn',
                   'test_subdir/test_cc-pvdz.1.element.json':    'H-Ar,Ca-Kr',
                   'test_aug-pcj-1.1.table.json':                'H-Ar',
                   'test_cc-pvdz.1.table.json':                  'H-Ar,Ca-Kr',
                   'test_def2-ecp.1.table.json':                 'Rb-Rn',
                   'test_def2-tzvp.1.table.json':                'H-Rn'
}
# yapf: enable


def test_add_basis(tmp_path):
    tmp_path = str(tmp_path)  # Needed for python 3.5
    for sf, refs in _source_data.items():
        sf_path = os.path.join(auth_data_dir, sf)

        name = sf.split('.')[0]
        curate.add_basis(sf_path, tmp_path, 'test_subdir', 'test_' + name, 'test_basis_' + name, 'test_family',
                         'orbital', 'Test Basis Description: ' + name, '1', 'Test Basis Revision Description',
                         'Test Source', refs)

    md = api.get_metadata(tmp_path)
    assert len(md) == len(_source_data)

    # Re-read
    for sf in _source_data.keys():
        name = name = sf.split('.')[0]
        name = 'test_basis_' + name
        bse_dict = api.get_basis(name, data_dir=tmp_path)

        assert bse_dict['family'] == 'test_family'

        # Compare against the file we created from
        sf_path = os.path.join(auth_data_dir, sf)
        assert curate.compare_basis_against_file(name, sf_path, data_dir=tmp_path)

        # Check that all the files exist and contain the right elements
        for fpath, elements in _expected_files.items():
            fpath = os.path.join(tmp_path, fpath)
            assert os.path.isfile(fpath)

            fdata = fileio.read_json_basis(fpath)
            expect_elements = set(misc.expand_elements(elements, True))
            assert set(fdata['elements'].keys()) == expect_elements

    # Validate the new data dir
    validator.validate_data_dir(tmp_path)

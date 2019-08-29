"""
Tests BSE curation functions
"""

import os
import tempfile

from basis_set_exchange import curate, api, validator, misc, fileio, compose, memo
from basis_set_exchange.curate.readers import g94
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
        assert curate.compare_basis_against_file(name, sf_path, data_dir=tmp_path) == True

        # Check that all the files exist and contain the right elements
        for fpath, elements in _expected_files.items():
            fpath = os.path.join(tmp_path, fpath)
            assert os.path.isfile(fpath)

            fdata = fileio.read_json_basis(fpath)
            expect_elements = set(misc.expand_elements(elements, True))
            assert set(fdata['elements'].keys()) == expect_elements

    # Validate the new data dir
    validator.validate_data_dir(tmp_path)

def test_g94_reader_reference():
    tmp_file = '''! test file for testing multiple elements referencing to the same internal basis set
! and a mixture of internal and external basis set for the same element
-Li     0 
def2SVP
D   1   1.00
      0.2300000              1.0000000        
D   1   1.00
      0.0757000              1.0000000        
F   1   1.00
      0.1350000              1.0000000        
S 1 1.00
 6.98698293267e-03 1.0
P 1 1.00
 2.73333333333e-02 1.0
****
-Be -B  -C  -N  -O  -F  -Ne 0 
def2SVP
****'''
    bs_data = g94.read_g94(tmp_file.split('\n'), None)
    # test if the external data is read
    assert bs_data['elements']['3']['electron_shells'][5]['exponents'][0][:4] == '0.23'
    # test if the internal data is read
    assert bs_data['elements']['3']['electron_shells'][0]['exponents'][0][:4] == '266.'
    # test if all elements are being read
    assert bs_data['elements']['10']['electron_shells'][0]['exponents'][0][:4] == '3598'

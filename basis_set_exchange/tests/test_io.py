"""
Tests for the BSE IO functions
"""

# Most functionality is covered under other tests.
# This tests the remainder

import os
import pytest

from basis_set_exchange import fileio, api
from .common_testvars import data_dir


# yapf: disable
@pytest.mark.parametrize('file_path', ['cc-pVDZ.0.table.json',
                                       'CRENBL.0.table.json',
                                       'dunning/cc-pVDZ.1.element.json',
                                       'crenb/CRENBL.0.element.json',
                                       'dunning/cc-pVDZ.1.json',
                                       'crenb/CRENBL.0.json',
                                       'crenb/CRENBL-ECP.0.json'])
# yapf: enable
def test_read_write_basis(file_path):
    # needed to be tested to make sure something isn't left
    # out of the sort lists, etc
    full_path = os.path.join(data_dir, file_path)
    full_path_new = full_path + '.new'
    data = fileio.read_json_basis(full_path)
    fileio.write_json_basis(full_path_new, data)
    os.remove(full_path_new)


@pytest.mark.parametrize('file_path', ['REFERENCES.json'])
def test_read_write_references(file_path):
    # needed to be tested to make sure something isn't left
    # out of the sort lists, etc
    full_path = os.path.join(data_dir, file_path)
    full_path_new = full_path + '.new'
    data = fileio.read_references(full_path)
    fileio.write_references(full_path_new, data)
    os.remove(full_path_new)

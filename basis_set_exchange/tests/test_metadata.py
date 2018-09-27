"""
Tests for BSE metadata
"""

import tempfile
import json
import os

from basis_set_exchange import api, curate

_data_dir = api._default_data_dir


def test_get_metadata():
    api.get_metadata()


def test_metadata_uptodate():
    old_metadata = os.path.join(_data_dir, 'METADATA.json')

    # Create a temporary file
    new_metadata_tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    new_metadata = new_metadata_tmp.name
    new_metadata_tmp.close()

    curate.create_metadata_file(new_metadata, _data_dir)

    with open(old_metadata, 'r') as f:
        old_data = json.load(f)
    with open(new_metadata, 'r') as f:
        new_data = json.load(f)

    os.remove(new_metadata)

    assert old_data == new_data

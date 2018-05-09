"""
Tests for BSE metadata
"""

import os
import bse
import json

data_dir = bse.default_data_dir

def test_get_metadata():
    bse.get_metadata()


def test_metadata_uptodate():
    old_metadata = os.path.join(data_dir, 'METADATA.json')
    new_metadata = os.path.join(data_dir, 'METADATA.json.new')
    bse.curate.create_metadata_file(new_metadata, data_dir)

    with open(old_metadata, 'r') as f:
        old_data = json.load(f)
    with open(new_metadata, 'r') as f:
        new_data = json.load(f)

    os.remove(new_metadata)

    assert old_data == new_data

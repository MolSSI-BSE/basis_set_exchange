"""
Tests for BSE metadata
"""

import os
import hashlib
import bse
from bse import curate

data_dir = bse.default_data_dir

def test_get_metadata():
    bse.get_metadata()


def test_metadata_uptodate():
    old_metadata = os.path.join(data_dir, 'METADATA.json')
    new_metadata = os.path.join(data_dir, 'METADATA.json.new')
    curate.create_metadata_file(new_metadata, data_dir)

    with open(old_metadata, 'rb') as f:
        old_hash = hashlib.sha1(f.read()).hexdigest()
    with open(new_metadata, 'rb') as f:
        new_hash = hashlib.sha1(f.read()).hexdigest()

    os.remove(new_metadata)

    if old_hash != new_hash:
        print("Old hash: ", old_hash)
        print("New hash: ", new_hash)
        raise RuntimeError("Metadata does not appear to be up to date")

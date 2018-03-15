"""
Validation tests for the data
"""

import bse
import glob
import os

data_dir = bse.default_data_dir

def test_valid():
    # Validate all the data files in the data directory
    # against their respective schemas
    filelist = glob.glob(data_dir + "/*.json")
    filelist.extend(glob.glob(data_dir + "/*/*.json"))

    for f in filelist:
        if f.endswith('METADATA.json'):
            continue
        if f.endswith('REFERENCES.json'):
            bse.validate('references', f)
        elif f.endswith('.table.json'):
            bse.validate('table', f)
        elif f.endswith('.element.json'):
            bse.validate('element', f)
        else:
            bse.validate('component', f)

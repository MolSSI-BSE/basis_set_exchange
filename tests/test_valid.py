"""
Validation tests for the data
"""

import bse
import glob
import pytest
import os

bse_path = bse.__path__[0]
data_dir = os.path.join(bse_path, 'data')

def test_valid():
    # Validate all the data files in the data directory
    # against their respective schemas
    filelist = glob.glob(data_dir + "/*.json")
    filelist.extend(glob.glob(data_dir + "/*/*.json"))

    for f in filelist:
        if f.endswith('REFERENCES.json'):
            bse.validate('references', f)
        elif f.endswith('.table.json'):
            bse.validate('table', f)
        elif f.endswith('.element.json'):
            bse.validate('element', f)
        else:
            bse.validate('component', f)

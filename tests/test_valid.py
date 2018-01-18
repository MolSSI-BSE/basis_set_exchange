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
    filelist = glob.glob(data_dir + "/*.json")

    for f in filelist:
        #print("validating ", f)
        if f.endswith('REFERENCES.json'):
            continue
        if f.endswith('.table.json'):
            bse.validate('table', f)
        elif f.endswith('.element.json'):
            bse.validate('element', f)
        else:
            bse.validate('component', f)

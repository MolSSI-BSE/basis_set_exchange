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
    component_list = [ f for f in filelist if not 'element' in f and not 'table' in f ]

    for f in component_list:
        bse.validate('component', f)

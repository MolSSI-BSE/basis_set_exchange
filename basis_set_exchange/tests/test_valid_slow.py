"""
Test for validating the formatting of the json files
"""

import glob
import os
import pytest

from basis_set_exchange import validator
from .common_testvars import data_dir


def test_valid_data_dir():
    validator.validate_data_dir(data_dir)

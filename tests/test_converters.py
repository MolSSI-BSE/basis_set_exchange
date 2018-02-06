"""
Tests for converting to basis set formats
"""

import bse

def test_converters():
    formats = bse.converters.converter_map
    bs_metadata = bse.get_metadata()

    for bs_name in bs_metadata.keys():
        bs_data = bse.get_basis_set(bs_name)

        # loop over all formats and give it a try
        for name,func in formats.items():
            func(bs_data)

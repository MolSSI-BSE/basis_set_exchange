"""
Tests for lookups of elemental data
"""

import pytest
from basis_set_exchange import lut, api
from .common_testvars import bs_metadata

ecp_basis_sets = [k for k,v in bs_metadata.items() if 'scalar_ecp' in v['functiontypes']] 

@pytest.mark.slow
@pytest.mark.parametrize('basis_name', ecp_basis_sets)
def test_stored_nelec_start_slow(basis_name):
    bs_data = api.get_basis(basis_name) 

    for el in bs_data['elements'].values():
        if not 'ecp_electrons' in el:
            continue

        ecp_electrons = el['ecp_electrons']
        starting_shells = lut.electron_shells_start(ecp_electrons, 8)

        # Make sure the number of covered electrons matches
        nelec_sum = 0 
        for am,count in enumerate(starting_shells):
            # How many shells of AM are covered by the ECP
            covered = count - 1

            # Adjust for the principal quantum number where the shells for the AM start
            # (ie, p start at 2, d start at 3)
            covered -= am

            # Number of orbs = 2*am+1. Multiply by 2 to get electrons
            nelec_sum += (2*am+1)*2*covered

        assert nelec_sum == ecp_electrons
        

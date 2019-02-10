'''
Functions for helping curate BSE basis set data
'''

from .skel import create_skel
from .readers import read_formatted_basis
from .metadata import create_metadata_file
from .add_basis import add_basis
from .compare_ref import compare_basis_against_ref
from .printing import (print_electron_shell, print_ecp_pot, print_element, print_component_basis, print_element_basis,
                       print_table_basis)
from .compare import (compare_electron_shells, electron_shells_are_subset, electron_shells_are_equal, compare_ecp_pots,
                      ecp_pots_are_subset, ecp_pots_are_equal, compare_elements, compare_basis, shells_difference,
                      potentials_difference, subtract_electron_shells)

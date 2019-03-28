'''
Functions for helping curate BSE basis set data
'''

from .skel import create_skel
from .readers import read_formatted_basis, get_reader_formats
from .metadata import create_metadata_file
from .add_basis import add_basis
from .compare_report import compare_basis_against_file, compare_basis_files, compare_basis_sets
from .compare import (compare_electron_shells, electron_shells_are_subset, electron_shells_are_equal, compare_ecp_pots,
                      ecp_pots_are_subset, ecp_pots_are_equal, compare_elements, compare_basis, shells_difference,
                      potentials_difference, subtract_electron_shells)
from .misc import elements_in_files, component_file_refs
from .graph import view_graph, make_graph_file
from .diff import diff_basis_dict, diff_json_files

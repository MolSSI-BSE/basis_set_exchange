"""
Functions for helping curate BSE basis set data
"""

from .metadata import create_metadata_file
from .add_basis import add_basis, add_basis_from_dict, add_from_components
from .compare_report import (
    basis_comparison_report,
    compare_basis_against_file,
    compare_basis_files,
    compare_basis_sets,
    shells_difference,
    potentials_difference,
)
from .compare import (
    compare_electron_shells,
    electron_shells_are_subset,
    electron_shells_are_equal,
    compare_ecp_pots,
    ecp_pots_are_subset,
    ecp_pots_are_equal,
    compare_elements,
    compare_basis,
)
from .misc import elements_in_files, component_file_refs
from .graph import view_graph, make_graph_file
from .diff import diff_basis_dict, diff_json_files

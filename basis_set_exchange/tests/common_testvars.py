'''
Some data common to all tests
'''

import os
import basis_set_exchange as bse

# The directory containing this file
_my_dir = os.path.dirname(os.path.abspath(__file__))

# Use random for getting sets of elements
rand_seed = 39466  # from random.org

# Load all the metadata once
data_dir = bse.api._default_data_dir
bs_metadata = bse.get_metadata()
bs_names = bse.get_all_basis_names()
bs_formats = list(bse.get_formats().keys()) + [None]
ref_formats = list(bse.get_reference_formats().keys()) + [None]
all_families = bse.get_families()
all_roles = bse.get_roles()
true_false = [True, False]

# All basis names/versions combinations
bs_names_vers = []
for k, v in bs_metadata.items():
    for ver in v['versions'].keys():
        bs_names_vers.append((k, ver))

# Directory with some fake data
fake_data_dir = os.path.join(_my_dir, 'fakedata')

# Directory with authoritative sources
auth_data_dir = os.path.join(_my_dir, 'sources')

# Directory with other testing data
test_data_dir = os.path.join(_my_dir, 'test_data')

# All files in the data dir
all_files = bse.fileio.get_all_filelist(data_dir)
all_metadata_files = all_files[0]
all_table_files = all_files[1]
all_element_files = all_files[2]
all_component_files = all_files[3]

# Full paths to all the files
all_file_paths = [[os.path.join(data_dir, x) for x in y] for y in all_files]
all_metadata_paths = all_file_paths[0]
all_table_paths = all_file_paths[1]
all_element_paths = all_file_paths[2]
all_component_paths = all_file_paths[3]

# A representative sample of basis sets
bs_names_sample = ['6-31g', '6-31+g*', 'aug-cc-pvtz', 'lanl2dz', 'def2-tzvp', 'jorge-tzp', 'sto-3g', 'fano-qz']


def bool_matrix(size):
    '''Returns an identity matrix of a given size consisting of bool types
    '''
    ret = [[False for i in range(size)] for j in range(size)]
    for x in range(size):
        ret[x][x] = True
    return ret

# Copyright (c) 2017-2022 The Molecular Sciences Software Institute, Virginia Tech
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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
bs_names = list(bs_metadata.keys())
bs_read_formats = list(bse.get_reader_formats().keys())
bs_write_formats = list(bse.get_writer_formats()) + [None]
bs_write_formats_ecp = list(bse.get_writer_formats(['scalar_ecp']).keys()) + [None]
bs_write_formats_noecp = list(set(bs_write_formats) - set(bs_write_formats_ecp))
ref_formats = list(bse.get_reference_formats().keys()) + [None]
all_families = bse.get_families()
all_roles = bse.get_roles()
true_false = [True, False]

# All basis names/versions combinations
bs_names_vers = []
for k, v in bs_metadata.items():
    for ver in v['versions'].keys():
        bs_names_vers.append((k, ver))

# Directory the CLI executables
_parent_dir = os.path.abspath(os.path.join(_my_dir, os.pardir))
cli_dir = os.path.join(_parent_dir, 'cli')

# Directory with some fake data
fake_data_dir = os.path.join(_my_dir, 'fakedata')

# Directory with authoritative sources
auth_data_dir = os.path.join(_my_dir, 'sources')

# Directory with files for testing curation functions
curate_test_data_dir = os.path.join(_my_dir, 'curate_test_data')

# Directory with files for testing readers
reader_test_data_dir = os.path.join(_my_dir, 'reader_test_data')

# Directory with files for testing the validator
validator_test_data_dir = os.path.join(_my_dir, 'validator_test_data')

# Directory with files for testing geometric augmentation
diffuse_augmentation_test_data_dir = os.path.join(_my_dir, 'diffuse_augmentation')
steep_augmentation_test_data_dir = os.path.join(_my_dir, 'steep_augmentation')

# Directory with files for testing removal of free primitives
rmfree_test_data_dir = os.path.join(_my_dir, 'rm_free')

# Directory with files for testing truhlar calenderization
truhlar_test_data_dir = os.path.join(_my_dir, 'truhlar')

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
bs_names_sample_noecp = ['6-31g', '6-31+g*', 'aug-cc-pvtz', 'jorge-tzp', 'sto-3g', 'fano-qz']

# Authoritative data in the sources dir
auth_src_map = {}
for x in os.listdir(auth_data_dir):
    if not x.endswith('.bz2'):
        continue

    # remove .fmt.bz2
    base, _ = os.path.splitext(x)
    base, _ = os.path.splitext(base)

    if base in auth_src_map:
        raise RuntimeError("Duplicate basis set in authoritative sources: {}".format(base))

    auth_src_map[base] = os.path.join(auth_data_dir, x)


def bool_matrix(size):
    '''Returns an identity matrix of a given size consisting of bool types
    '''
    ret = [[False for i in range(size)] for j in range(size)]
    for x in range(size):
        ret[x][x] = True
    return ret

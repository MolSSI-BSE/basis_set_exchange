'''
Some data common to all tests
'''

import basis_set_exchange as bse

# Use random for getting sets of elements
rand_seed = 39466 # from random.org

# Load all the metadata once
bs_metadata = bse.get_metadata()
bs_names = bse.get_all_basis_names()
bs_formats = list(bse.get_formats().keys())
ref_formats = list(bse.get_reference_formats().keys())
true_false = [ True, False ]

# A representative sample of basis sets
bs_names_sample = ['6-31g', '6-31+g*', 'aug-cc-pvtz',
                   'lanl2dz', 'def2-tzvp', 'tzp', 'sto-3g']

# To test role lookup
role_tests = [ ('cc-pvdz', 'rifit', 'cc-pvdz-rifit'),
               ('cc-pvtz', 'rifit', 'cc-pvtz-rifit'),
               ('cc-pvqz', 'rifit', 'cc-pvqz-rifit'),
               ('aug-cc-pvdz', 'rifit', 'aug-cc-pvdz-rifit'),
               ('aug-cc-pvtz', 'rifit', 'aug-cc-pvtz-rifit'),
               ('aug-cc-pvqz', 'rifit', 'aug-cc-pvqz-rifit')
             ]


def bool_matrix(size):
    '''Returns an identity matrix of a given size consisting of bool types
    '''
    ret = [[False for i in range(size)] for j in range(size)]
    for x in range(size):
        ret[x][x] = True
    return ret

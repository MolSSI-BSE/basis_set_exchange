#!/usr/bin/env python3

import argparse
import json
import os
import sys

from bse_ng.basis_io import *
from bse_ng.lut import *


parser = argparse.ArgumentParser()
parser.add_argument('file1', help='First JSON file', type=str)
parser.add_argument('file2', help='Second JSON file', type=str)
args = parser.parse_args()

bs1 = read_json_basis_file(args.file1)
bs2 = read_json_basis_file(args.file2)


# Compare the elements
bse1 = bs1['basisSetElements']
bse2 = bs2['basisSetElements']

elkeys1 = set(bse1.keys())
elkeys2 = (bse2.keys())

common = elkeys1.intersection(elkeys2)
bse1_only = elkeys1 - elkeys2
bse2_only = elkeys2 - elkeys1

same_elements = set()
different_elements = set()

for z in common:
    el1 = bse1[z]
    el2 = bse2[z]

    if el1 == el2:
        same_elements.add(z)
    else:
        different_elements.add(z)


print("SUMMARY:")
print("             First basis: {} : {}".format(args.file1, bs1['basisSetName']))
print("            Second basis: {} : {}".format(args.file2, bs2['basisSetName']))
print("           Same in both files: ", same_elements)
print(" In both files, but different: ", different_elements)
print("          Only in first basis: ", bse1_only)
print("         Only in second basis: ", bse2_only)


#!/usr/bin/env python3

import argparse
import json
import os
import sys

from bse_ng.converters import bse_xml 


parser = argparse.ArgumentParser()
parser.add_argument('xmlfile', help='XML file to convert', type=str)
args = parser.parse_args()

def pprint(d):
    print(json.dumps(d, indent=4))

bsdict = bse_xml.read_basis_xml(args.xmlfile)

# Create the new file
outfile = bse_xml.create_json_path(args.xmlfile)

with open(outfile, 'w') as f:
    json.dump(bsdict, f, indent=4)


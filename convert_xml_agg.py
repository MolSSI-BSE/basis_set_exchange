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

bsdict = bse_xml.read_agg_xml(args.xmlfile)
quit()

# Create the new file
bsdir = os.path.dirname(args.xmlfile)

filebase = os.path.splitext(args.xmlfile)[0]
outfile = "{}_{}.json".format(filebase, bsdict['basisSetRegion'])
outfile = os.path.join(bsdir, outfile)


with open(outfile, 'w') as f:
    json.dump(bsdict, f, indent=4)


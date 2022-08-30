#!/usr/bin/env python3

'''
Obtaining basis set data as JSON and converting to a python dictionary
'''

import os
import requests

# This is the main url of the BSE API
# THIS WILL CHANGE TO HTTPS IN THE FUTURE
# HTTPS IS RECOMMENDED
main_bse_url = "http://basissetexchange.org"

# This allows for overriding the URL via an environment variable
# Feel free to just use the base_url below
base_url = os.environ.get('BSE_API_URL', main_bse_url)


############################################
# Change the user agent and 'from' headers
############################################

# Change these to something more
# descriptive if you would like. This lets us know
# how many different people/groups are using the site

# Valid email is COMPLETELY OPTIONAL. Put whatever
# you would like in there, or leave it as is. If you
# do put your email there, we will never give it
# away or email you, except in case we think errors in
# your script are causing us problems.
headers = {
    'User-Agent': 'BSE Example Python Script',
    'From': 'bse@molssi.org'
}


###############################################################
# Get the metadata for all elements
###############################################################
r = requests.get(base_url + '/api/metadata',
                 headers=headers
                )

# List of all basis sets
metadata = r.json()
print(metadata.keys())


###############################################################
# Get the def2-QZVP basis for all elements in json format
# Note that basis set names and formats are not case sensitive
###############################################################
r = requests.get(base_url + '/api/basis/def2-qzvpd/format/json',
                 headers=headers
                )

# The basis set data is stored in r.json
basis_dict = r.json()
print(basis_dict['name'])

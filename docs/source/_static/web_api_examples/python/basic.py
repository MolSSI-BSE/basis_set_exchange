#!/usr/bin/env python3

import os
import requests

# This is the main url of the BSE API
# THIS WILL CHANGE TO HTTPS IN THE FUTURE
# HTTPS IS RECOMMENDED
main_bse_url = "http://basissetexchange.org"

# This allows for overriding the URL via an environment variable
# Feel free to just use the base_url below
base_url = os.environ.get('BSE_API_URL', main_bse_url)


def print_results(r):
    '''Checks for errors and prints the results of a request'''

    # r.text will contain the formatted output as a string
    print(r.text)
    if r.status_code != 200:
        raise RuntimeError("Could not obtain data from the BSE. Check the error information above")



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
# Get the def2-QZVP basis for all elements in nwchem format
# Note that basis set names and formats are not case sensitive
###############################################################
r = requests.get(base_url + '/api/basis/def2-qzvpd/format/nwchem',
                 headers=headers
                )

print_results(r)


######################################################################
# Get the cc-pvqz basis for hydrogen and carbon in gaussian94 format
######################################################################
# Elements can be passed a variety of ways. Here, I'm just
# passing a list of Z numbers. See elements.py for other ways
# you can specify elements
params = {'elements': [1, 6, 7]}
r = requests.get(base_url + '/api/basis/cc-pvqz/format/psi4',
                 params=params,
                 headers=headers
                )

print_results(r)

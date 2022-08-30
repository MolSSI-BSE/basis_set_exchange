#!/bin/bash

set -e

# Example of using the Basis Set Exchange REST API
# with wget

MAIN_BSE_URL="http://basissetexchange.org"

# See if the BSE_API_URL environment variable is set
# If it is, use that as the URL
if [ -z "${BSE_API_URL}" ]
then 
   BASE_URL="${MAIN_BSE_URL}" 
else
   BASE_URL="${BSE_API_URL}"
fi

USER_AGENT="BSE Example Bash Script"
FROM="bse@molssi.org"

# This outputs to a file called basis.nw
wget -U "${USER_AGENT}" --header="From: ${FROM}" "${BASE_URL}/api/basis/cc-pvtz/format/nwchem/?elements=1,4&elements=2" -O basis.nw

# Get the references for above (in bibtex)
wget -U "${USER_AGENT}" --header="From: ${FROM}" "${BASE_URL}/api/references/cc-pvtz/format/bib/?elements=1,4&elements=2" -O basis_refs.bib

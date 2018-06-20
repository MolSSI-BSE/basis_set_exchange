[![Build Status](https://travis-ci.org/MolSSI-BSE/basis_set_exchange.svg?branch=master)](https://travis-ci.org/MolSSI-BSE/basis_set_exchange)
[![codecov](https://codecov.io/gh/MolSSI-BSE/basis_set_exchange/branch/master/graph/badge.svg)](https://codecov.io/gh/MolSSI-BSE/basis_set_exchange)

**Warning - This project is still under heavy development.**

## Overview
This project is used to form the backend of the new Basis Set Exchange.

This project is a collaboration between the Molecular Sciences Software Institute (http://www.molssi.org)
and the Environmental Molecular Sciences Laboratory (https://www.emsl.pnl.gov)

## Documentation

Full user and developer documentation can be found at https://molssi-bse.github.io/basis_set_exchange

## Installation
To do a local install of the Python directory,
```
pip install -e .
```

## Testing
Tests can be run using `py.test -v` once installed.

## Examples
```
import basis_set_exchange as bse

# Obtain the STO-3G basis set in nwchem format (as a string) for hydrogen and carbon
bse.get_basis('STO-3G', elements=[1,6], fmt='nwchem')

# Obtain the references for the above
bse.get_references('STO-3G', elements=[1,6], fmt='txt')
```

## License

This project is released under the BSE 3-Clause license. See LICENSE for details.

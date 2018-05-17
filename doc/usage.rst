Quickstart and Basic Usage
==============================================

Installation
-------------------

The BSE can be installed with `pip`

For example, to install in to the current directory, `pip install -e .`

Importing
-------------------

All end-user functionality is available by importing the `bse` module.

Getting a basis set
-------------------

The main function for getting a basis set is :func:`bse.api.get_basis`.
Output format is controlled by the `fmt` parameter. By default, a python
dictionary is returned. If a format is specified, a string is returned
instread.::

  import bse

  # Get a basis set as a python dictionary
  bs_dict = bse.get_basis('6-31G*')

  # Same as above, but in gaussian format (as a string)
  bs_str = bse.get_basis('6-31G*', fmt='gaussian94')
  print(bs_str)

  # Available formats are available via get_formats
  print(bse.get_formats())


By default, all elements for which the basis set is defined are included - this
can be overridden with the `elements` parameter.::

  # Get only carbon and oxygen
  bse.get_basis('aug-cc-pvtz', elements=[6,8])


Getting references
------------------

Reference/citations can be obtained via :func:`bse.api.get_references`. The `elements`
parameter is similar to that in :func:`bse.api.get_basis`.

The `fmt` parameter controls the output format. By default, the output
is a dictionary. If `fmt` is specified, the output is a string.::

  # Get references for 6-31G*, all elements, as a dictionary
  bse.get_references('6-31G*')

  # Restrict to hydrogen and fluorine
  bse.get_references('6-31G*', elements=[1,9])

  # In bibtex
  bib = bse.get_references('6-31G*', fmt='bib', elements=[1,9])

  # Available formats are available via get_reference_formats
  print(bse.get_reference_formats())


Versioning
-------------------

Basis sets within the package are versioned. This allows for changes to be made to a
basis set, while keeping the old data accessible for historical purposes.
Versions are specified by integers. By default,
v0 will match the original BSE data.

Versions are meant to be increased only when there is a material change to the data.
If data is simply being added (new elements), the version will not be incremented.

Both `bse.api.get_basis` and :func:`bse.api.get_references` accept a `version` parameter.
If `version` is not specified, the latest version is used.::

  # Get latest version
  bs_str = bse.get_basis('6-31G*', fmt='gaussian94')

  # Get the original BSE data
  bs_str = bse.get_basis('6-31G*', version=0, fmt='gaussian94')

Metadata
-------------------

TODO

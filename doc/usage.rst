Quickstart and Basic Usage
==============================================

.. testsetup:: *

   import bse


Installation
-------------------

The BSE can be installed with `pip`

For example, to install in to the current directory, `pip install -e .`

Importing
-------------------

All end-user functionality is available by importing the `bse` module.

Getting a basis set
-------------------

The main function for getting a basis set is :func:`bse.get_basis`.
Output format is controlled by the `fmt` parameter. By default, a python
dictionary is returned. If a format is specified, a string is returned
instread.

.. doctest::

   >>> # Get a basis set as a python dictionary
   >>> bs_dict = bse.get_basis('6-31G*')
   >>> bs_dict['basis_set_name']  
   '6-31G*'

   >>> # Basis set names are case insensitive
   >>> bs_dict = bse.get_basis('6-31g*')
   >>> bs_dict['basis_set_name']  
   '6-31G*'

   >>> # Same as above, but in gaussian format (as a string)
   >>> bs_str = bse.get_basis('6-31G*', fmt='gaussian94')
   >>> print(bs_str)
   ****
   H     0
   S   3   1.00
        18.731137               0.0334946
         2.8253944              0.2347269
   ...


   >>> # Available formats are available via get_formats
   >>> bse.get_formats()
   {'json': 'JSON', 'nwchem': 'NWChem', 'gaussian94': 'Gaussian94'}


By default, all elements for which the basis set is defined are included - this
can be overridden with the `elements` parameter

.. doctest::

   >>> # Get only carbon and oxygen
   >>> bs_str = bse.get_basis('aug-cc-pvtz', elements=[6,8], fmt='nwchem')
   >>> print(bs_str)
   BASIS "ao basis" PRINT
   #BASIS SET: (11s,6p,3d,2f) -> [5s,4p,3d,2f]
   C    S
      8236.0000000              0.0005310             -0.0001130              0.0000000              0.0000000
   ...

   >>> # Can also use strings with the element symbols (and be mixed with integers)
   >>> # and integers as strings
   >>> bs_str = bse.get_basis('aug-cc-pvtz', elements=['C', 8, 'Ne', '16'], fmt='nwchem')
   >>> print(bs_str)
   BASIS "ao basis" PRINT
   #BASIS SET: (11s,6p,3d,2f) -> [5s,4p,3d,2f]
   C    S
      8236.0000000              0.0005310             -0.0001130              0.0000000              0.0000000
   ...


Getting references
------------------

Reference/citations can be obtained via :func:`bse.get_references`. The `elements`
parameter is similar to that in :func:`bse.get_basis`.

The `fmt` parameter controls the output format. By default, the output
is a dictionary. If `fmt` is specified, the output is a string.

.. doctest::
   >>> # Get references for 6-31G*, all elements, as a list of dictionaries
   >>> refs = bse.get_references('6-31G*')
   >>> print(refs[0])
   {'reference_info': [{'reference_description': ...
 
   >>> # As bibtex, restricting to H and F
   >>> bib = bse.get_references('6-31G*', fmt='bib', elements=[1,9])
   >>> print(bib)
   % H
   %     31G valence double-zeta
   %         ditchfield1971a
   %
   % F
   %     6-31G valence double-zeta
   %         hehre1972a
   %
   %     Polarization functions associated with 6-31G
   %         hariharan1973a
   %
   <BLANKLINE> 
   <BLANKLINE> 
   @article{ditchfield1971a,
       author = {R. Ditchfield and W. J. Hehre and J. A. Pople},
       title = {Self-Consistent Molecular-Orbital Methods. IX. An Extended Gaussian-Type Basis for Molecular-Orbital Studies of Organic Molecules},
       journal = {J. Chem. Phys.},
       volume = {54},
       page = {724-728},
       year = {1971},
       doi = {10.1063/1.1674902}
   }
   ...


   >>> # Available formats are available via get_reference_formats
   >>> bse.get_reference_formats()
   {'json': 'JSON', 'bib': 'BibTeX', 'txt': 'Plain Text'}


Versioning
-------------------

Basis sets within the package are versioned. This allows for changes to be made to a
basis set, while keeping the old data accessible for historical purposes.
Versions are specified by integers. By default,
v0 will match the original BSE data.

Versions are meant to be increased only when there is a material change to the data.
If data is simply being added (new elements), the version will not be incremented.

Both `bse.get_basis` and :func:`bse.get_references` accept a `version` parameter,
which is a string. If `version` is not specified, the latest version is used.

.. doctest::

   >>> # Get latest version
   >>> bs_str = bse.get_basis('6-31G*', fmt='gaussian94')

   >>> # Get the original BSE data
   >>> bs_str = bse.get_basis('6-31G*', version='0', fmt='gaussian94')

   >>> # Versions can also be passed as integers
   >>> bs_str = bse.get_basis('6-31G*', version=0, fmt='gaussian94')


Lookup by Role
--------------

Many basis sets have auxiliary basis sets for different purposes (density fitting,
for example). These auxiliary basis sets can be queried in the BSE
using the :func:`bse.lookup_basis_by_role`. This function takes the
primary basis set and the role you wish to look up. The function
returns the name of the basis set.

Like the other functions, the basis name and role are not
case sensitive.

.. doctest::

   >>> # Find the MP2-fit basis set for cc-pvtz
   >>> bse.lookup_basis_by_role('cc-pvtz', 'mp2fit')
   'cc-pvtz-mp2fit'
 

Metadata
-------------------

The BSE contains metadata for all the basis sets that is in its data directory.
This information can be accessed by the :func:`bse.get_metadata` function

.. note:: Note that the key is the name of the basis set that has been transformed
          into some internal name (see :func:`bse.transform_basis_name`)

A simple list containing all the basis set names can be obtained via :func:`bse.get_all_basis_names`

.. doctest::

   >>> # Get the metadata
   >>> md = bse.get_metadata()
 
   >>> # What is the latest version of 6-31G
   >>> md['6-31g']['latest_version']
   '1'
 
   >>> # All versions of 6-31G
   >>> md['6-31g']['versions'].keys()
   dict_keys(['0', '1'])

   >>> # Elements defined in v0
   >>> md['6-31g']['versions']['0']['elements']
   ['1', '2', '3', '4', '5', '6',...
 
   >>> # Print all the basis sets known to the BSE
   >>> all_bs = bse.get_all_basis_names()
   >>> print(all_bs)
   ['3-21g', '4-31g', '5-21g', ...


Basis set and family notes
--------------------------------

Notes about a basis set or a basis set family can be obtained, also.

.. doctest::

   >>> # Notes from a basis (name is case insensitive)
   >>> bse.get_basis_notes('6-31g')
   'Notes are not available for the 6-31g basis'

   >>> # Get the family of a basis set from the metadata
   >>> fam = bse.get_basis_family('6-31G**')
   >>> fam
   'pople'

   >>> # Get family notes (not case sensitive)
   >>> bse.get_family_notes('pople')
   'Notes about Pople basis sets...


Memoization
--------------------------------

By default, the library will memoize/cache some internal data. This has a big effect when,
for example, running :func:`bse.get_basis` with the same basis set name (even if choosing
different elements and options).

For most uses, this can be left enabled - memory usage will still be very low, even if reading
many basis sets. If you wish, it can be disabled by setting :attr:`bse.memoize_enabled` to `False`.
Note that this does not clear any existing cache.


   >>> # Default is enabled
   >>> bse.memoize_enabled
   True

   >>> # Manually disable it
   >>> bse.memoize_enabled = False
   >>> bse.memoize_enabled
   False

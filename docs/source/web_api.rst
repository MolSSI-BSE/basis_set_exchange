REST API Reference
==================

.. testsetup:: *

   import requests
   import os
   BASE_URL = os.environ["BSE_API_URL"]

Below is a list of all public API endpoints. Examples shown are in python
(using the `requests <http://docs.python-requests.org/en/master/>`_ module).
However, any software or command-line tool that can access APIs like this (curl, wget, etc) can also be used.

Basis set names, formats, and reference formats are case insensitive.

Note that the API is read-only, and does not allow for uploading or modifying data. 


Note about headers
------------------

Additional header information (user agent, email) are optional. However,
if you would like to share who you are or what you are doing, feel free to
add these fields. We will not use the email for any purpose other than to
notify you if your scripts are broken and causing us problems.

Any data collected from user agent or email will not be shared outside of
MolSSI, other than in aggregate form.


Specifying Elements
-------------------

Some endpoints take a string specifying which elements data should be obtained for.
string is a comma-separated list of element symbols and/or Z numbers. Ranges can also be used.

Symbols are not case sensitive and can be mixed with Z-numbers.

Examples:
    * ``H-Ne`` - for hydrogen through neon (inclusive)
    * ``1-10`` - same as above
    * ``C,8,p-17`` - carbon, oxygen, phosphorus through chlorine

Elements can also be passed as multiple ``element`` parameters

    * ``?elements=1&elements=6&elements=n`` - hydrogen, carbon, nitrogen



``/api/metadata``
-----------------

Returns JSON representing the metadata about the basis sets contained in the BSE.

.. code-block:: python

   >>> r = requests.get(BASE_URL + '/api/metadata')
   >>> print(r.json())
   {'3-21g': ... 



``/api/formats``
----------------

Returns JSON representing which basis set formats are available, along with a description

.. code-block:: python

   >>> r = requests.get(BASE_URL + '/api/formats')
   >>> print(r.json())
   {'bsedebug': 'BSE Debug', 'cfour': 'CFOUR',... 


   
``/api/reference_formats``
--------------------------

Similar to ``/api/formats``, but has info about which reference formats are supported

.. code-block:: python

   >>> r = requests.get(BASE_URL + '/api/reference_formats')
   >>> print(r.json())
   {'bib': 'BibTeX', 'json': 'JSON',...



``/api/basis/<basis_name>/format/<fmt>``
----------------------------------------

Obtain basis set data. This is the main function of the basis set exchange.

The output is a string, except when ``<fmt>`` is json. Basis names are not case sensitive.
See ``/api/metadata`` for getting a list of basis sets. Formats can be obtained with ``/api/formats``.

For how to pass elements, see `Specifying Elements`_

Several options are available. These are specified as GET paramters

+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Option                   | Arguments         | Description                                                                                                                                                                    | 
+==========================+===================+================================================================================================================================================================================+
| elements                 | String            | Restrict the output to only certain elements (see `Specifying Elements`_)                                                                                                      |
+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| version                  | Integer           | Obtain a specific version of the basis set. Default is latest version                                                                                                          |
+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| uncontract_general       | 1,0 or true,false | Remove general contractions                                                                                                                                                    |
+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| uncontract_segmented     | 1,0 or true,false | Remove general and segmented contractions                                                                                                                                      |
+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| uncontract_spdf          | 1,0 or true,false | Split apart combined sp, spd, etc, shells                                                                                                                                      |
+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| optimize_general         | 1,0 or true,false | Optimize general contractions. See the `library documentation <https://molssi-bse.github.io/basis_set_exchange/developer_api.html#basis_set_exchange.manip.optimize_general>`_ |
+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| make_general             | 1,0 or true,false | Make the basis set as generally-contracted as possible                                                                                                                         |
+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| header                   | 1,0 or true,false | If false, do not print the BSE information header in the output                                                                                                                |
+--------------------------+-------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. code-block:: python

   >>> # Get STO-3G as json
   >>> r = requests.get(BASE_URL + '/api/basis/sto-3g/format/json')
   >>> print(r.json())
   {'name': 'STO-3G', 'names': ['STO-3G'], 'flags': [], 'family': 'sto', 'description': 'STO-3G Minimal Basis (3 functions/AO)',...

   >>> # Get 6-31G in nwchem format, getting only hydrogen, carbon, nitrogen, and oxygen
   >>> r = requests.get(BASE_URL + '/api/basis/6-31g/format/nwchem/?elements=1,6-8')
   >>> print(r.text)
   #----------------------------------------------------------------------
   # Basis Set Exchange
   # Version ...
   # https://www.basissetexchange.org
   #----------------------------------------------------------------------
   #   Basis set: 6-31G
   # Description: 6-31G valence double-zeta
   #        Role: orbital
   #     Version: 1  (Data from Gaussian 09/GAMESS)
   #----------------------------------------------------------------------
   <BLANKLINE>
   <BLANKLINE>
   BASIS "ao basis" SPHERICAL PRINT
   #BASIS SET: (4s) -> [2s]
   H    S
         0.1873113696E+02       0.3349460434E-01
         0.2825394365E+01       0.2347269535E+00
         0.6401216923E+00       0.8137573261E+00
   H    S
         0.1612777588E+00       1.0000000
   #BASIS SET: (10s,4p) -> [3s,2p]
   C    S
         0.3047524880E+04       0.1834737132E-02
         0.4573695180E+03       0.1403732281E-01
         0.1039486850E+03       0.6884262226E-01
         0.2921015530E+02       0.2321844432E+00
         0.9286662960E+01       0.4679413484E+00
         0.3163926960E+01       0.3623119853E+00
   C    SP
         0.7868272350E+01      -0.1193324198E+00       0.6899906659E-01
         0.1881288540E+01      -0.1608541517E+00       0.3164239610E+00
         0.5442492580E+00       0.1143456438E+01       0.7443082909E+00
   C    SP
         0.1687144782E+00       0.1000000000E+01       0.1000000000E+0


``/api/references/<basis_name>/format/<fmt>``
---------------------------------------------

Obtain basis set data. This is the main function of the basis set exchange.

The output is a string, except when ``<fmt>`` is json. Basis names are not case sensitive.
See ``/api/metadata`` for getting a list of basis sets. Formats can be obtained with ``/api/reference_formats``.

For how to pass elements, see `Specifying Elements`_

Several options are available. These are specified as GET paramters

+--------------------------+-------------------+-----------------------------------------------------------------------------+
| Option                   | Arguments         | Description                                                                 | 
+==========================+===================+=============================================================================+
| elements                 | String            | Restrict the output to only certain elements (see `Specifying Elements`_)   |
+--------------------------+-------------------+-----------------------------------------------------------------------------+
| version                  | Integer           | Obtain a specific version of the basis set. Default is latest version       |
+--------------------------+-------------------+-----------------------------------------------------------------------------+

.. code-block:: python

   >>> # Get references for aug-cc-pvtz as json
   >>> r = requests.get(BASE_URL + '/api/references/aug-cc-pvtz/format/json')
   >>> print(r.json())
   [{'reference_info': [{'reference_description': 'The cc-pVTZ basis set', 'reference_data'...

   >>> # Same as above, but in bibtex
   >>> r = requests.get(BASE_URL + '/api/references/aug-cc-pvtz/format/bib')
   >>> print(r.text)
   %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   ...
   @article{balabanov2005a,
       author = {Balabanov, Nikolai B. and Peterson, Kirk A.},
       title = {Systematically convergent basis sets for transition metals. I. All-electron correlation consistent basis sets for the 3d elements Sc-Zn},
       journal = {J. Chem. Phys.},
       volume = {123},
       pages = {064107},
       year = {2005},
       doi = {10.1063/1.1998907}
   }
   <BLANKLINE>
   @article{dunning1989a,
       author = {Dunning, Thom H.},
       title = {Gaussian basis sets for use in correlated molecular calculations. I. The atoms boron through neon and hydrogen},
       journal = {J. Chem. Phys.},
       volume = {90},
       pages = {1007-1023},
       year = {1989},
       doi = {10.1063/1.456153}
   }
   <BLANKLINE>
   @article{kendall1992a,
       author = {Kendall, Rick A. and Dunning, Thom H. and Harrison, Robert J.},
       title = {Electron affinities of the first-row atoms revisited. Systematic basis sets and wave functions},
       journal = {J. Chem. Phys.},
       volume = {96},
       pages = {6796-6806},
       year = {1992},
       doi = {10.1063/1.462569}
   }
   ...
   


``/api/notes/<basis_name>``
---------------------------

Obtain notes about a basis set. Output is plain text.

   >>> # Get notes for 6-31g
   >>> r = requests.get(BASE_URL + '/api/notes/6-31g')
   >>> print(r.text)
   --------------------------------------------------------------------------------
      Original BSE Contributor: Dr. David Feller
               Original BSE PI: (none)
    Original BSE Last Modified: Thu, 24 Apr 2008 00:05:19 GMT
   --------------------------------------------------------------------------------
   <BLANKLINE>
   Notes from the original BSE
   ===========================
   <BLANKLINE>
   The 6-31G basis set uses 6 Gaussian primitives to expand the 1s core of second
   period elements.
   ...



``/api/family_notes/<family>``
------------------------------

Obtain notes about a family of basis sets. Output is plain text.

   >>> # Get notes for the jensen family
   >>> r = requests.get(BASE_URL + '/api/family_notes/jensen')
   >>> print(r.text)
   Notes about the Jensen basis sets
   =================================
   <BLANKLINE>
   admm basis sets
   ------------------------
   The most widely used approach to approximate the Coulomb and exchange integrals is density fitting, also known as the resolution-of-the-identity (RI) approximation.
   In this, the products of two one-electron basis functions are expanded in one-center auxiliary functions. RI significantly improves performance with a limited impact on
   the accuracy and has therefore been applied to HF/KS theory as well as correlated methods. ADMM has been developed specifically for the exchange contribution. The exchange
   energy is split into two parts. On consisting of the exact HF exchange and the second is a first-order correction term, evaluated as the difference between the generalized
   gradient approximation exchange in the full and auxiliary basis sets.
   <BLANKLINE>
   <BLANKLINE>
   aug-pc-n and  pc-n basis sets (where n indicates the level of polarization beyond the atomic system)
   ...

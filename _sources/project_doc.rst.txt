Project Planning and Documents
==============================================

This page contains the plans and outlines the new Basis Set Exchange
project.


Goal
-------------------
A rewrite of the current EMSL Basis Set Exchange database and website (https://www.basissetexchange.org)


Public Code Repository
-----------------------

The main code for this project is located on GitHub at
https://github.com/MolSSI-BSE/basis_set_exchange.  Comments and
bugs/issues should be reported there.

The main documentation is located at https://molssi-bse.github.io/basis_set_exchange

Additional related projects are located under the MolSSI-BSE GitHub
organization at https://github.com/MolSSI-BSE


Background
-------------------

The Basis Set Exchange has served the community well since its inception
around 2004. However, the current code stack is considered outdated and
in need of a rewrite.

* The code is currently written in Java, which is considered 'heavy' for
  such a project today.

* The codebase is considered over-engineered in other ways, including
  the use of multiple components originally written for other projects
  and repurposed for the BSE

The actual basis set data is considered de-facto standard by much of the
community. Nevertheless, there are errors and inconsistencies. While most
errors are believed to be fixed, some may remain due to some inflexibility
of the current code stack.


Proposed Components
-------------------

The new BSE is proposed to have 4 separate components

1. A store or database of basis set data, in some form
2. A library accompanying the data, allowing for querying and composing basis
   set information
3. An web API for programmatically querying and obtaining basis set data
4. A web frontend


Backend Data Store
******************

This component contains the actual basis set data in a common format. The
old BSE stored basis set data in XML files, while the new BSE will
use JSON files, making it more lightweight.  This data will be stored
in a publicly-accessible git repository on GitHub. This repository is
combined with the backend library (see next section). Since the data is
stored as (relatively) plain text, modifications to this data can take
place through already-established channels and protocols dealing with
modifications and conflict resolution (GitHub issues and pull requests,
for example). Many people working with basis sets will be familiar with
such procedures, and additional help and perhaps web interfaces should
be available to those that are not familiar.


Backend Library
*******************

This library is responsible for consuming the raw basis set data and
producing some useful output. Some aspects of this include:

* Composing complete basis sets from components (for example, adding polarization or diffuse functions)
* Converting a basis set to a particular output format (Gaussian or NWChem, for example)
* Helper functions for curation
* Schemas and validation functions
* Basis set manipulation, such as uncontraction and optimization of general contractions.
* Obtaining notes about basis sets and basis set families
* Obtaining references for basis sets

Due to the nature of this library, it is combined (in the same version
control repository) with the raw basis set data. While this is likely
the best path forward, discussion of separation of the data and the
library may happen at a later date.

In addition, a command-line interface will also be included as part of this library.


Public API (REST API)
*********************

This component is responsible for allowing users to programmatically
obtain basis set information via a REST interface.

This interface will mostly mirror the main API of the backend library.

It should be noted that this interface will be read-only, as the curation
of the basis set raw data is done elsewhere.


Web Frontend
*******************

Many people currently use the web frontend to download and explore
basis sets. In general, people approve of the current interface and
functionality, with only small improvements desired.

The web fronted should be as separate as possible from the other
components, allowing for future changes and possible rewrites.


Data Curation and Identifiers
------------------------------

As part of this project, basis sets will be verified, when possible,
against other databases, literature, and what is implemented in various
codes. An effort will be made to identify canonical, standard values
based on these sources. When differences are found, they will be recorded
within the basis set data notes.

This work will support the community in running well-defined, reproducible
computations.


Education
------------------------------

A section of the website will be devoted to education about basis sets,
including common nomenclature and the best basis sets for different
calculations.


Project Members
-------------------

The project is a collaboration between MolSSI and EMSL/PNNL. The members
and major responsibilities are:

* MolSSI

  * Benjamin Pritchard - Original project lead, development of backend library
  * Susi Lehtola - Maintainer of backend library, basis set curator
  * Doaa Altaraway - Development of the web frontend
  * Daniel Smith - Programming support

* EMSL

  * Tara Gibson - EMSL lead, development support
  * Phil Gackle - Sysadmin/Advisor
  * Eric Bylaska - Subject matter expert

* Other

  * Theresa Windus - Liaison, MolSSI BoD Sponsor, development support
  * Ellie Fought - Basis set curation support


Community Engagement
--------------------

Help from the community will likely be required for some parts of
the project. In particular, curation and validation of the basis data
itself will likely be a community-wide effort, as well as opinions on
website design.

In addition, opinions about basis set data and naming will be solicited
from basis set authors and the developers of computational chemistry code.

If you would like to help with this project, contact Benjamin Pritchard
at bpp4@vt.edu

Timelines and Milestones
------------------------

Current short-to-medium term milestones can be viewed at
https://github.com/MolSSI-BSE/basis_set_exchange/milestones

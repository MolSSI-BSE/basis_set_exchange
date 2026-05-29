.. _auxgen:

Automatic auxiliary basis set generation
========================================

The :mod:`basis_set_exchange.auxgen` subpackage implements the
pivoted-Cholesky procedure for automatically generating a primitive
auxiliary (density-fitting / resolution-of-the-identity) basis set
from a given orbital basis, following

* S. Lehtola, *Straightforward and accurate automatic auxiliary basis
  set generation for molecular calculations with atomic orbital basis
  sets*, J. Chem. Theory Comput. **17**, 6886 (2021),
  https://doi.org/10.1021/acs.jctc.1c00607.
* S. Lehtola, *Automatic generation of accurate and cost-efficient
  auxiliary basis sets*, J. Chem. Theory Comput. **19**, 6242 (2023),
  https://doi.org/10.1021/acs.jctc.3c00670.

The closed-form one-center Coulomb integrals are taken from R. M. Pitzer,
*Atomic self-consistent-field program by the basis set expansion
method: Columbus version*, Comput. Phys. Commun. **170**, 239 (2005),
https://doi.org/10.1016/j.cpc.2005.04.003.

The generated basis is written in the standard BSE component-format
schema; any of the format writers available in the rest of the library
can therefore be used to emit the result.


Algorithm overview
------------------

For each element the orbital basis is decontracted to primitives
:math:`\chi_\mu(r) = r^{n_\mu} Y_{l_\mu m_\mu}(\hat r)\,e^{-\alpha_\mu r^2}`.
Spherical and Cartesian shells are both accepted: a Cartesian shell of
nominal angular momentum :math:`L` contributes spherical components at
:math:`l = L, L-2, \ldots,` all sharing the same radial power
:math:`n = L`.  ECP entries on the element are ignored.

For every unordered pair of primitives :math:`(\mu, \nu)` (with the
diagonal :math:`\mu = \nu` included) and every
angular momentum :math:`L \in \{|l_\mu - l_\nu|, |l_\mu - l_\nu| + 2,
\ldots, l_\mu + l_\nu\}` (real-Gaunt parity), a candidate auxiliary
function is generated.  The product radial form
:math:`r^{n_\mu + n_\nu} e^{-(\alpha_\mu + \alpha_\nu) r^2}` is mapped
to a standard primitive :math:`r^L e^{-\alpha_{\rm eff} r^2}` using the
``<r>``-matching transformation of the 2021 paper (Appendix II eq 16),

.. math::

   \alpha_{\rm eff} = \left[
     \frac{\Gamma(L+2)\,\Gamma(n_{\rm rad}+\tfrac{3}{2})}
          {\Gamma(L+\tfrac{3}{2})\,\Gamma(n_{\rm rad}+2)}
   \right]^2 (\alpha_\mu + \alpha_\nu),

with :math:`n_{\rm rad} = n_\mu + n_\nu`.  The candidates are then
gathered per :math:`L` into a Coulomb-overlap metric (paper eq 7),
normalized to unit diagonal, and thinned by pivoted Cholesky.

Two variants of the four-index pre-screening are supported:

* ``scheme='basic'``: every primitive pair is taken as a candidate.
* ``scheme='reduced'`` *(default)*: shell-pair-driven pivoted Cholesky
  of the four-index ``(μν|ρσ)`` tensor is performed first to thin the
  list of contributing orbital shell-pairs.  Within a chosen
  shell-pair, all m-resolved components are added together as in the
  ERKALE implementation.

To make the most of the unit-diagonal candidate metric (where the
first pivot is degenerate), each :math:`L` block runs pivoted Cholesky
under three ordering families and keeps the shortest pivot set:

1. linear order (insertion order of the candidates),
2. increasing off-diagonal-norm presort (paper Sect. 3),
3. ``n_random`` independent random permutations (the Note Added in
   Proof of the 2021 paper).

The drop tolerance ``τ`` is applied directly to the residual diagonal
of the Cholesky factorisation (absolute threshold).

Two optional refinements from the 2023 paper are available:

* ``contract=True`` applies the SVD-based general contraction
  (Section 2.1 of the 2023 paper).  Per :math:`l`, the
  ``W = J^T J = V^{-1/2} I^T I V^{-1/2}`` matrix is formed from the
  three-index integrals :math:`I_{\mu\nu, A} = (\mu\nu | A)` and the
  two-index Coulomb metric :math:`V_{AB} = (A|B)`; its eigenvectors
  with eigenvalues above the threshold ``ε`` define general
  contractions of the primitive auxiliary basis.
* ``prune_lmax=True`` drops shells above the
  :math:`l_{\rm keep} = \max(2 l_{\rm occ}^{\max},
  l_{\rm occ}^{\max} + l_{\rm OBS}^{\max} + l_{\rm inc})` cap of the
  2023 paper, eq 9.  The default :math:`l_{\rm occ}^{\max}` follows
  the row-based table of the paper (0 for H/He, 1 for
  :math:`Z \le 18`, 2 for :math:`Z \le 54`, 3 otherwise).


Command-line interface
----------------------

The ``bse autogen-aux`` subcommand reads an orbital basis from a file
and writes the generated auxiliary basis to a file::

    bse autogen-aux <input_file> <output_file>
        [--in-fmt FMT] [--out-fmt FMT]
        [--threshold 1e-7]
        [--scheme {basic,reduced}]
        [--n-random 100] [--seed 0]
        [--contract] [--contract-threshold 1e-4]
        [--prune-lmax] [--linc 1]

Input and output formats are auto-detected from the file extension
unless overridden.  All standard BSE writers (NWChem, Molcas, Psi4,
Turbomole, JSON, ...) are accepted on the output side.

Example: build an auxiliary basis for hydrogen, carbon, and oxygen
from cc-pVDZ at a tight :math:`\tau = 10^{-7}` tolerance::

    bse get-basis cc-pVDZ nwchem --elements H,C,O > /tmp/ccpvdz.nw
    bse autogen-aux /tmp/ccpvdz.nw /tmp/ccpvdz_aux.nw --threshold 1e-7

Add the SVD contraction and high-angular-momentum prune::

    bse autogen-aux /tmp/ccpvdz.nw /tmp/ccpvdz_aux_contracted.nw \
        --threshold 1e-7 --contract --prune-lmax


Python API
----------

The high-level entry point produces a BSE component-format basis dict:

.. code-block:: python

    import basis_set_exchange as bse
    from basis_set_exchange.auxgen import generate_auxiliary_basis

    orbital = bse.get_basis('cc-pVDZ', elements=[1, 6, 8])

    aux = generate_auxiliary_basis(
        orbital,
        threshold=1.0e-7,
        scheme='reduced',
        n_random=100,
        contract=False,
        prune_lmax=False,
    )

    # `aux` is a dict in the BSE component schema; emit any format:
    print(bse.write_formatted_basis_str(aux, 'nwchem'))

A per-element entry point is also exported for use cases that already
have an element dict to hand:

.. code-block:: python

    from basis_set_exchange.auxgen.auxgen import (
        generate_auxiliary_basis_for_element,
    )

    aux_c = generate_auxiliary_basis_for_element(
        orbital['elements']['6'],
        threshold=1.0e-7,
        scheme='reduced',
    )


Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 22 12 66

   * - Parameter
     - Default
     - Description
   * - ``threshold``
     - ``1e-7``
     - Pivoted-Cholesky drop tolerance :math:`\tau` (absolute, applied
       to the residual diagonal).  The same tolerance is used for the
       four-index pre-screening (reduced scheme) and the per-L
       candidate Cholesky.
   * - ``scheme``
     - ``'reduced'``
     - ``'basic'`` enumerates all orbital primitive pairs as
       candidates; ``'reduced'`` first thins them with a shell-pair-
       driven pivoted Cholesky of the four-index ERI tensor.  The
       2023 paper recommends ``'reduced'``.
   * - ``n_random``
     - ``100``
     - Number of random orderings tried in the per-L candidate
       Cholesky.  In addition the linear order and the off-diagonal-
       norm presort are always tried; the smallest pivot set across
       all attempts is kept.  Setting ``n_random = 0`` reproduces the
       paper's deterministic baseline.
   * - ``seed``
     - ``0``
     - Seed for the random orderings, for reproducibility.
   * - ``contract``
     - ``False``
     - Apply the SVD-based general contraction of the 2023 paper.
   * - ``contract_threshold``
     - ``1e-4``
     - Eigenvalue cutoff :math:`\epsilon` for keeping contractions.
   * - ``prune_lmax``
     - ``False``
     - Drop shells with :math:`L > l_{\rm keep}` per the 2023 paper
       eq 9.
   * - ``linc``
     - ``1``
     - Increment :math:`l_{\rm inc}` in the pruning rule.


Notes
-----

* The generated auxiliary basis is always spherical; this matches the
  convention adopted by the 2021 paper and by most quantum chemistry
  programs.  Cartesian input shells are supported (with their radial
  contamination correctly tracked) but produce spherical output.
* Sympy is used only for the real-spherical Gaunt coefficients in
  :mod:`basis_set_exchange.auxgen.gaunt`, and is lazy-imported.  The
  radial integrals are evaluated with a pure closed form (no sympy at
  runtime).
* The PySCF-based test
  ``basis_set_exchange/tests/test_auxgen.py::test_eri_full_tensor_vs_pyscf_spd``
  cross-checks every one-center primitive ``(ab|cd)`` integral over
  an s/p/d basis against ``libcint`` to machine precision.

# Copyright (c) 2026 Susi Lehtola
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Driver for the automatic auxiliary basis generation procedure of
Lehtola, J. Chem. Theory Comput. 17, 6886 (2021)
[https://doi.org/10.1021/acs.jctc.1c00607], optionally augmented with
the contraction and pruning of Lehtola, J. Chem. Theory Comput. 19,
6242 (2023) [https://doi.org/10.1021/acs.jctc.3c00670].

Two variants of the basic algorithm are supported:

  * ``scheme='basic'``: enumerate every orbital primitive product
    (mu, nu) and every coupling L; the candidate pool for L is the set
    of (l_rad, alpha_rad) = (l_mu + l_nu, alpha_mu + alpha_nu) values.

  * ``scheme='reduced'`` (default, per the 2023 paper): pre-screen the
    orbital products with a pivoted Cholesky decomposition of the
    four-index (mu nu | rho sigma) tensor.  The surviving pairs feed
    into the same candidate-pool construction.

In both cases a pivoted Cholesky decomposition of the normalized
candidate Coulomb-overlap matrix (Lehtola 2021, eq 7) is performed for
each L; the candidates are pre-sorted by increasing off-diagonal norm
(Lehtola 2021, Sect. 3) to seed the decomposition from the most
linearly independent direction.  Each surviving candidate is converted
into a standard primitive r^L e^{-alpha_eff r^2} via the effective
exponent formula (Lehtola 2021, Appendix II eq 16).

The contraction step (``contract=True``) performs an SVD of the
orthogonalized three-index ERI tensor per L block (Lehtola 2023,
Sect. 2.1).  The pruning step (``prune_lmax``) drops shells above an
``l_max`` derived from the orbital basis (Lehtola 2023, Sect. 2.2,
eq 9).
"""

import numpy as np

from .. import skel, lut
from .pivchol import pivoted_cholesky, block_pivoted_cholesky
from .products import (
    decontract_primitives,
    candidate_pool_from_primitives,
    candidate_pool_from_pairs,
    primitive_product_pairs,
)
from .twoel import normalized_metric, product_metric


# ---------------------------------------------------------------------------
# Pivoted-Cholesky helpers
# ---------------------------------------------------------------------------

def _sort_by_offdiag_norm(S):
    """Return the order of indices in increasing off-diagonal row norm
    (Lehtola, J. Chem. Theory Comput. 17, 6886 (2021),
    https://doi.org/10.1021/acs.jctc.1c00607, Section 3): functions
    most likely linearly independent are placed first.
    """
    n = S.shape[0]
    if n <= 1:
        return list(range(n))
    norms = np.abs(S).sum(axis=1) - np.abs(np.diag(S))
    return list(np.argsort(norms))


def _pivot_with_order(S, order, tol):
    """Apply a specific permutation to S, run pivoted Cholesky, and
    translate the pivots back to the original indices.
    """
    Sp = S[np.ix_(order, order)]
    pivots, _ = pivoted_cholesky(Sp, tol=tol)
    return [order[p] for p in pivots]


def _most_compact_pivot(S, tol, n_random=100, seed=0):
    """Run pivoted Cholesky on S under several orderings and return the
    most compact pivot list, matching ERKALE's
    ``cholesky_pick_exponents`` (Lehtola, J. Chem. Theory Comput. 17,
    6886 (2021), https://doi.org/10.1021/acs.jctc.1c00607).

    Three orderings are tried in turn:

      1. **Linear** order (just the original index sequence).
      2. **Off-diagonal-norm presort** -- ascending column sum of S
         (paper Sect. 3), seeding the Cholesky with the function that
         has the smallest overlap with the rest of the candidates and
         is therefore least likely to be linearly dependent ("screening
         for linear dependence").
      3. **Random shuffles** -- ``n_random`` independent permutations
         (paper Note Added in Proof).

    The smallest pivot set across all orderings is returned.  The
    candidate metric has unit diagonal so the first-pivot choice is
    degenerate; different orderings update the residuals differently
    and yield different rank-revealing sequences.

    Parameters
    ----------
    S : numpy.ndarray
        Symmetric positive (semi-)definite block.
    tol : float
        Cholesky drop tolerance.
    n_random : int
        Number of random permutations to try.  Set to 0 to use only
        the linear ordering and the off-diagonal-norm presort.
    seed : int
        Seed for the random shuffles, for reproducibility.

    Returns
    -------
    list of int
        Selected pivot indices in the original ordering.
    """
    n = S.shape[0]
    if n == 0:
        return []
    if n == 1:
        return [0]

    rng = np.random.default_rng(seed)

    orders = [list(range(n)),                  # linear
              _sort_by_offdiag_norm(S)]        # off-diagonal-norm screen
    for _ in range(n_random):
        perm = list(range(n))
        rng.shuffle(perm)
        orders.append(perm)

    best = None
    best_pivots = None
    for order in orders:
        pivots = _pivot_with_order(S, order, tol)
        k = len(pivots)
        if best is None or k < best:
            best = k
            best_pivots = pivots
            if best == 0:
                break

    return best_pivots if best_pivots is not None else []


# ---------------------------------------------------------------------------
# Reduced-scheme 4-index pre-screening
# ---------------------------------------------------------------------------

def _reduced_pair_screen(primitives, threshold):
    """Shell-pair-driven pivoted Cholesky on the 4-index
    ``(mu nu | rho sigma)`` metric (Lehtola, J. Chem. Theory Comput. 17,
    6886 (2021), https://doi.org/10.1021/acs.jctc.1c00607).

    The metric is built over the full set of m-resolved primitive pairs,
    but pivot selection is shell-pair-driven (ERKALE convention): when
    the largest residual diagonal belongs to some m-pair, every other
    m-pair of the same orbital shell-pair is added as a pivot before
    the next greedy selection.  This guarantees that a chosen
    ``(l_a, n_a, alpha_a, l_b, n_b, alpha_b)`` shell-pair contributes
    *all* of its (2 l_a + 1)(2 l_b + 1) m-resolved products to the
    downstream candidate pool, as the algorithm intends.
    """
    pairs = primitive_product_pairs(primitives)
    if not pairs:
        return []
    M = product_metric(pairs)
    # Block identifier per pair index: the orbital shell-pair, ignoring m.
    block_of = []
    for (la, na, _ma, aa), (lb, nb, _mb, ab) in pairs:
        block_of.append((int(la), int(na), float(aa),
                         int(lb), int(nb), float(ab)))
    pivots, _ = block_pivoted_cholesky(M, block_of, tol=threshold)
    return [pairs[i] for i in pivots]


# ---------------------------------------------------------------------------
# Basis dict assembly
# ---------------------------------------------------------------------------

def _primitive_shells(per_L_alphas):
    """One BSE shell per primitive (segmented uncontracted)."""
    shells = []
    for L in sorted(per_L_alphas):
        for a in per_L_alphas[L]:
            shells.append({
                'function_type': 'gto_spherical',
                'region': '',
                'angular_momentum': [int(L)],
                'exponents': ["{:.10E}".format(a)],
                'coefficients': [["1.0000000000"]],
            })
    return shells


def _contracted_shells(per_L_contractions):
    """``per_L_contractions[L]`` is ``(exps, [gen1, gen2, ...])``."""
    shells = []
    for L in sorted(per_L_contractions):
        exps, gens = per_L_contractions[L]
        shells.append({
            'function_type': 'gto_spherical',
            'region': '',
            'angular_momentum': [int(L)],
            'exponents': ["{:.10E}".format(a) for a in exps],
            'coefficients': [["{:.10E}".format(c) for c in gen] for gen in gens],
        })
    return shells


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

def _select_per_L(pool, threshold, n_random=100, seed=0):
    """Per-L pivoted Cholesky on the standard primitive Coulomb-overlap
    metric (ERKALE convention).

    The candidate pool already holds ``alpha_eff`` exponents: each
    candidate represents a standard primitive r^L e^{-alpha_eff r^2}
    Y_{L M}.  The metric is :func:`twoel.primitive_aux_metric` rescaled
    to unit diagonal (since auxiliary functions are normalized so
    ``(A|A) = 1`` per Lehtola 2021, Sect. 2).

    ``n_random > 0`` activates the ERKALE Note-Added-in-Proof variant:
    try the off-diagonal-norm presort plus ``n_random`` random
    orderings and keep the most compact pivot set.  The default
    ``n_random = 0`` reproduces the paper's published algorithm.

    Returns ``{L: [alpha_eff, ...]}`` containing only the selected
    candidates, sorted decreasing.
    """
    out = {}
    for L, alphas in pool.items():
        if not alphas:
            continue
        S = normalized_metric(L, alphas)
        sel = _most_compact_pivot(S, tol=threshold, n_random=n_random,
                                  seed=seed + 1000 * L)
        if sel:
            out[L] = sorted((alphas[i] for i in sel), reverse=True)
    return out


def generate_auxiliary_basis_for_element(element_basis,
                                         threshold=1.0e-7,
                                         scheme='reduced',
                                         n_random=100,
                                         seed=0,
                                         contract=False,
                                         contract_threshold=1.0e-4,
                                         prune_lmax=False,
                                         linc=1,
                                         lmax_occ=None):
    """Generate an auxiliary basis for a single element.

    Parameters
    ----------
    element_basis : dict
        BSE-schema element basis dict.
    threshold : float
        Drop tolerance tau for the pivoted Cholesky decompositions.
        Tau = 1e-7 (the 2021 paper's tight setting) is the default.
    scheme : {'basic', 'reduced'}
        ``'basic'`` enumerates all orbital products; ``'reduced'``
        pre-screens products with a 4-index Cholesky.  The 2021 paper
        recommends ``'reduced'``.
    n_random : int
        Number of random candidate orderings to try per L when running
        the (unit-diagonal) basic-step pivoted Cholesky; the most
        compact pivot set is kept (Lehtola 2021 Note Added in Proof).
        Default 100.  Set to 0 to use only the linear and
        off-diagonal-norm orderings.
    seed : int
        Seed for the random shuffles, for reproducibility.
    contract : bool
        Apply the SVD-based contraction of Lehtola, J. Chem. Theory
        Comput. 19, 6242 (2023),
        https://doi.org/10.1021/acs.jctc.3c00670.
    contract_threshold : float
        Eigenvalue cutoff for keeping contractions (epsilon in the paper).
    prune_lmax : bool
        Apply the per-element angular-momentum pruning of 2023 eq 9.
    linc : int
        Increment parameter in eq 9 (default 1).
    lmax_occ : int, optional
        Maximum angular momentum of occupied shells used in eq 9.
        Required when ``prune_lmax=True`` and the per-element entry
        point is invoked directly (the public driver
        :func:`generate_auxiliary_basis` supplies it automatically
        from the row-based default table :func:`_default_lmax_occ`).

    Returns
    -------
    dict
        ``{'electron_shells': [...]}`` (no element-level metadata).
    """
    primitives = decontract_primitives(element_basis)
    if not primitives:
        return {'electron_shells': []}

    if scheme == 'reduced':
        sel = _reduced_pair_screen(primitives, threshold)
        pool = candidate_pool_from_pairs(sel)
    elif scheme == 'basic':
        pool = candidate_pool_from_primitives(primitives)
    else:
        raise ValueError("scheme must be 'basic' or 'reduced'")

    per_L_alphas = _select_per_L(pool, threshold, n_random=n_random, seed=seed)

    if prune_lmax:
        if lmax_occ is None:
            raise ValueError(
                "prune_lmax=True requires lmax_occ; pass it explicitly "
                "or use generate_auxiliary_basis() which supplies it from Z."
            )
        lmax_obs = max((l for (l, _n, _a) in primitives), default=0)
        l_keep = max(2 * lmax_occ, lmax_occ + lmax_obs + linc)
        per_L_alphas = {L: a for L, a in per_L_alphas.items() if L <= l_keep}

    if contract:
        from .contract import contract_aux
        contractions = contract_aux(primitives, per_L_alphas,
                                    contract_threshold=contract_threshold)
        shells = _contracted_shells(contractions)
    else:
        shells = _primitive_shells(per_L_alphas)

    return {'electron_shells': shells}


def _default_lmax_occ(z):
    """Default l_max of occupied shells per the 2023 paper (eq 9, after
    Yang et al.): 0 for H/He, 1 for Z<=18, 2 for Z<=54, 3 otherwise."""
    if z is None or z <= 2:
        return 0
    if z <= 18:
        return 1
    if z <= 54:
        return 2
    return 3


def generate_auxiliary_basis(orbital_basis,
                             elements=None,
                             threshold=1.0e-7,
                             scheme='reduced',
                             n_random=100,
                             seed=0,
                             contract=False,
                             contract_threshold=1.0e-4,
                             prune_lmax=False,
                             linc=1,
                             name=None,
                             description=None):
    """Generate an auxiliary basis (per element) from a BSE orbital basis.

    See :func:`generate_auxiliary_basis_for_element` for the meaning of
    the algorithmic parameters.
    """
    component = skel.create_skel('component')
    component['description'] = description or 'Auxiliary basis generated by basis_set_exchange.auxgen'
    component['data_source'] = name or 'auxgen'

    src_elements = orbital_basis['elements']

    if elements is None:
        zs = sorted(int(z) for z in src_elements.keys())
    else:
        zs = []
        for e in elements:
            if isinstance(e, int):
                zs.append(e)
            else:
                zs.append(lut.element_Z_from_sym(e))
        zs = sorted(set(zs))

    for z in zs:
        key = str(z)
        if key not in src_elements:
            continue
        eb = src_elements[key]
        out = generate_auxiliary_basis_for_element(
            eb,
            threshold=threshold,
            scheme=scheme,
            n_random=n_random,
            seed=seed,
            contract=contract,
            contract_threshold=contract_threshold,
            prune_lmax=prune_lmax,
            linc=linc,
            lmax_occ=_default_lmax_occ(z) if prune_lmax else None,
        )
        component['elements'][key] = out

    return component

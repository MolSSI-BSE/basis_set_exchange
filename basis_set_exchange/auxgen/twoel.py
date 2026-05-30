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
One-center two-electron integrals used by the auxgen pipeline.

Primitive Gaussians are described by ``(l, n, m, alpha)`` with the
unnormalized form

    chi_{l m n alpha}(r) = r^n Y_{l m}(\\Omega) e^{-alpha r^2},

so ``l`` is the angular momentum (controlling the Y_{l m} factor), and
``n`` is the radial power.  For spherical / regular GTOs ``n = l``;
cartesian shells of nominal angular momentum L contribute lower-l
components with ``n = L > l`` (the well-known cartesian
"contamination").

Three integral families are provided:

  * :func:`primitive_eri` -- the four-index (ab|cd) over normalized
    primitives.  Reference implementation used by the test suite
    (validated against PySCF's libcint to machine precision).

  * :func:`primitive_aux_metric` -- two-index (P|Q) between normalized
    standard primitives at a single L (the candidate metric used by
    the per-L Cholesky), and :func:`normalized_metric` which rescales
    it to unit diagonal.

  * :func:`product_metric` -- shell-pair-vectorised four-index metric
    over m-resolved product pairs, used by the reduced-scheme
    pre-screening.
"""

import numpy as np
from math import pi

from .gaunt import real_gaunt, coupling_lvals, gaunt_table
from .radial import radial_integral, gto_norm, gto_norm_array


# ---------------------------------------------------------------------------
# Reference 4-index ERI (used by tests; not in the hot path).
# ---------------------------------------------------------------------------

def primitive_eri(la, na, ma, alpha_a,
                  lb, nb, mb, alpha_b,
                  lc, nc, mc, alpha_c,
                  ld, nd, md, alpha_d):
    """(ab|cd) over overlap-normalized primitives of the form
    chi(r) = N r^n Y_{l m} e^{-alpha r^2}.

    Reference implementation: explicit sum over the multipole index L
    and projection M, no shell-level vectorisation.  Used by the test
    suite (cross-checked against PySCF/libcint to machine precision).
    The production pipeline uses :func:`product_metric` instead, which
    vectorises this same sum at the shell-pair level.
    """
    L_left = coupling_lvals(la, lb)
    L_right = coupling_lvals(lc, ld)
    Lset = tuple(L for L in L_left if L in L_right)
    if not Lset:
        return 0.0

    n_ab = na + nb
    n_cd = nc + nd
    alpha_ab = alpha_a + alpha_b
    alpha_cd = alpha_c + alpha_d

    total = 0.0
    for L in Lset:
        ang = 0.0
        for M in range(-L, L + 1):
            gl = real_gaunt(la, ma, lb, mb, L, M)
            if gl == 0.0:
                continue
            gr = real_gaunt(lc, mc, ld, md, L, M)
            if gr == 0.0:
                continue
            ang += gl * gr
        if ang == 0.0:
            continue
        rad = radial_integral(L, n_ab, n_cd, alpha_ab, alpha_cd)
        total += (4.0 * pi / (2 * L + 1)) * ang * rad

    Na = gto_norm(na, alpha_a)
    Nb = gto_norm(nb, alpha_b)
    Nc = gto_norm(nc, alpha_c)
    Nd = gto_norm(nd, alpha_d)
    return Na * Nb * Nc * Nd * total


# ---------------------------------------------------------------------------
# Single-L Coulomb metric between normalized standard primitives.
# ---------------------------------------------------------------------------

def primitive_aux_metric(L, alphas):
    """``(P|Q)`` between normalized standard primitives
    ``r^L Y_{L M} e^{-alpha r^2}`` sharing the same ``L`` (and ``M``).

    Symmetric, positive definite, M-independent.  Returns the metric in
    its natural (un-normalized) form; see :func:`normalized_metric` for
    the unit-diagonal variant used by the candidate Cholesky.
    """
    a = np.asarray(alphas, dtype=float)
    n = a.size
    if n == 0:
        return np.zeros((0, 0), dtype=float)
    A, B = np.meshgrid(a, a, indexing='ij')
    rad = radial_integral(L, L, L, A, B)
    Np = gto_norm_array(L, a)
    return (4.0 * pi / (2 * L + 1)) * Np[:, None] * Np[None, :] * rad


def normalized_metric(L, alphas):
    """Coulomb metric on standard primitives at angular momentum ``L``,
    rescaled to unit diagonal -- i.e. each primitive is implicitly
    re-normalized so that ``(A|A) = 1``, matching the convention of
    Lehtola, J. Chem. Theory Comput. 17, 6886 (2021)
    [https://doi.org/10.1021/acs.jctc.1c00607], eq 7.
    """
    M = primitive_aux_metric(L, alphas)
    if M.size == 0:
        return M
    d = np.sqrt(np.diag(M))
    return M / np.outer(d, d)


# ---------------------------------------------------------------------------
# Shell-pair-vectorised four-index Coulomb metric (reduced-scheme).
# ---------------------------------------------------------------------------


def product_metric(pairs):
    """Build the four-index Coulomb metric ``M[mu, nu] = (mu nu | rho sigma)``
    over m-resolved orbital primitive product pairs.

    The pairs are grouped by their orbital shell-pair
    ``(l_a, n_a, alpha_a, l_b, n_b, alpha_b)``.  For each shell-pair x
    shell-pair we form the full ``(2 l_a + 1)(2 l_b + 1)`` x
    ``(2 l_c + 1)(2 l_d + 1)`` block in one numpy ``einsum`` call,

        block[ma, mb, mc, md]
            = sum_L  (4 pi / (2 L + 1)) * R_L * sum_M G_left[ma, mb, L M]
                                                     G_right[mc, md, L M],

    times the orbital normalisations, and place it into the global
    metric.  Compared to the naive m-resolved loop, this moves the
    work from O(N_m_pair^2) Python iterations down to O(N_shell_pair^2)
    vectorised contractions.
    """
    n = len(pairs)
    M = np.zeros((n, n), dtype=float)
    if n == 0:
        return M

    # Group m-resolved pair indices by orbital shell-pair.
    sp_of = {}
    for idx, ((la, na, ma, aa), (lb, nb, mb, ab_)) in enumerate(pairs):
        sp_of.setdefault((la, na, aa, lb, nb, ab_), []).append((idx, ma, mb))

    # idx_grid[ma + la, mb + lb] -> global index in ``pairs``; -1 for missing.
    sp_keys = list(sp_of.keys())
    sp_idx_grid = {}
    for key in sp_keys:
        la, _na, _aa, lb, _nb, _ab = key
        grid = -np.ones((2*la + 1, 2*lb + 1), dtype=np.int64)
        for (idx, ma, mb) in sp_of[key]:
            grid[ma + la, mb + lb] = idx
        sp_idx_grid[key] = grid

    for ip, kp in enumerate(sp_keys):
        la, na, aa, lb, nb, ab_ = kp
        norm_p = gto_norm(na, aa) * gto_norm(nb, ab_)
        n_ab = na + nb
        a_ab = aa + ab_
        L_left = coupling_lvals(la, lb)
        idx_p = sp_idx_grid[kp]

        for iq in range(ip, len(sp_keys)):
            kq = sp_keys[iq]
            lc, nc, ac, ld, nd, ad = kq
            norm_q = gto_norm(nc, ac) * gto_norm(nd, ad)
            n_cd = nc + nd
            a_cd = ac + ad

            Lset = tuple(L for L in L_left if L in coupling_lvals(lc, ld))
            if not Lset:
                continue

            block = None
            for L in Lset:
                rad = radial_integral(L, n_ab, n_cd, a_ab, a_cd)
                if rad == 0.0:
                    continue
                kernel = (4.0 * pi / (2 * L + 1)) * rad
                contrib = kernel * np.einsum('abM,cdM->abcd',
                                             gaunt_table(la, lb, L),
                                             gaunt_table(lc, ld, L))
                block = contrib if block is None else block + contrib

            if block is None:
                continue
            block *= norm_p * norm_q

            # Scatter into the global metric.  All shells are fully
            # populated (every m-component present) by construction, so
            # the index grids contain no sentinels.
            idx_q = sp_idx_grid[kq]
            Na, Nb, Nc, Nd = block.shape
            row_idx = idx_p.reshape(-1)
            col_idx = idx_q.reshape(-1)
            block_flat = block.reshape(Na * Nb, Nc * Nd)
            M[np.ix_(row_idx, col_idx)] += block_flat
            if ip != iq:
                M[np.ix_(col_idx, row_idx)] += block_flat.T

    return M

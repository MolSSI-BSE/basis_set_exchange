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
Auxiliary basis contraction following Lehtola, J. Chem. Theory Comput.
19, 6242 (2023) [https://doi.org/10.1021/acs.jctc.3c00670], Section 2.1.

Per angular momentum l of the auxiliary basis:

  1. Build the two-index Coulomb-overlap V = (P|Q) over the surviving
     primitive aux Gaussians at angular momentum l.
  2. Build the m = 0 = m' subblock of the W matrix from eq 7 of the
     2023 paper,

         W_PQ = sum_{mu, nu, m_mu, m_nu} (mu nu | P)_{l, 0} (mu nu | Q)_{l, 0}

     (the spherical symmetry of the atomic sum makes the full W block
     diagonal in (l, m) and independent of m, so the m=0 slice carries
     all the information).
  3. Coulomb-normalize the primitives -- i.e. work in the unit-diagonal
     metric S = D^{-1} V D^{-1} (D = sqrt(diag V)) rather than the
     ill-conditioned raw metric V -- symmetrically orthogonalize S
     (dropping near-linearly-dependent directions), and diagonalize W
     in that orthonormal basis.  The eigenvalues lambda are the squared
     singular values of the orthogonalized three-index tensor; keep the
     eigenvectors with lambda >= epsilon.

  4. Convert the resulting contraction coefficients -- expressed in
     the Coulomb-normalized primitive basis -- to the overlap-normalized
     primitive convention printed by basis-set libraries, exactly as in
     ERKALE's ``basistool contractaux``:

         c = Wvec * sqrt(z)

     so the output is byte-comparable to ERKALE's reference.  The
     contracted functions are not separately renormalized to
     ``(A|A) = 1``; their overall per-contraction scale follows ERKALE's
     convention.

This mirrors ERKALE's ``basistool contractaux`` reference implementation,
with the methodological improvement that atomic spherical symmetry is
used to reduce the W matrix to its m = 0 slice (Section 2.1 of the 2023
paper), which is not exploited in ERKALE.
"""

import numpy as np
from math import pi, gamma

from .. import manip
from .gaunt import coupling_lvals, gaunt_table
from .radial import radial_integral, gto_norm_array
from .twoel import primitive_aux_metric


def orbital_aos(element_basis):
    """Enumerate the *contracted* spherical orbital basis functions of an
    element as ``[(l, alphas, weights), ...]``.

    Each entry is one contracted atomic orbital at angular momentum
    ``l``: ``alphas`` are its primitive exponents and ``weights`` are the
    contraction coefficients folded with the primitive normalization
    constants (so the radial density is ``sum_k weights[k] r^l
    e^{-alphas[k] r^2}``).  Combined ``sp``/``spd`` shells are split into
    single-``l`` shells first.

    The contraction step fits products of the *orbital basis functions*
    (the contracted AOs actually used in the SCF), not the decontracted
    primitives -- matching ERKALE's ``basistool contractaux``.  Building
    the W matrix from the decontracted primitives would inflate the
    orbital-product space and retain far too many auxiliary functions.

    Each AO is renormalized to ``<A|A> = 1`` (the standard convention
    chemistry programs apply on basis-set read).  This is the identity
    on contractions already stored as overlap-normalized in BSE, but it
    correctly handles bases whose stored coefficients do not satisfy
    ``<A|A> = 1`` (e.g. 3ZaPa-NR/He has an s shell with coefficient
    ``9.36e-4`` rather than ``1.0``); without this, the contracted AO
    contributes a vanishing weight to the W matrix and the SVD spectrum
    drifts noticeably from the ERKALE reference.
    """
    split = manip.uncontract_spdf({'elements': {'1': element_basis}},
                                  max_am=0, use_copy=True)['elements']['1']
    aos = []
    for sh in split['electron_shells']:
        l = sh['angular_momentum'][0]
        exps = np.array([float(e) for e in sh['exponents']], dtype=float)
        norms = gto_norm_array(l, exps)
        # Overlap metric of overlap-normalized primitives at this l.
        A, B = np.meshgrid(exps, exps, indexing='ij')
        Sov = norms[:, None] * norms[None, :] * 0.5 * gamma(l + 1.5) / (A + B)**(l + 1.5)
        for col in sh['coefficients']:
            c = np.array([float(x) for x in col], dtype=float)
            if not np.any(c):
                continue
            aa = float(c @ Sov @ c)
            if aa <= 0.0:
                continue
            scale = 1.0 / np.sqrt(aa)
            aos.append((l, exps, c * norms * scale))
    return aos


def _W_block(aos, L, alphas_P):
    """Build the m=0 subblock of W at angular momentum L,

        W_PQ = sum_{mu nu m_mu m_nu} (mu nu | P)_{L 0} (mu nu | Q)_{L 0},

    where ``mu, nu`` run over the *contracted* orbital AOs ``aos`` (as
    returned by :func:`orbital_aos`) and ``alphas_P`` are the aux
    exponents at this L (standard primitives r^L e^{-alpha_P r^2}).

    For an orbital AO pair the radial factor is the contraction-weighted
    sum over their primitive pairs,

        R_P = sum_{i in mu, j in nu} w_i w_j
                  R_L(l_mu + l_nu, alpha_i + alpha_j; L, alpha_P),

    (``w`` already folds in the primitive norms), and the angular factor
    is the M = 0 Gaunt slice.
    """
    nP = len(alphas_P)
    if nP == 0:
        return np.zeros((0, 0), dtype=float)
    aP = np.asarray(alphas_P, dtype=float)
    NP = gto_norm_array(L, aP)

    W = np.zeros((nP, nP), dtype=float)
    for (la, ea, wa) in aos:
        for (lb, eb, wb) in aos:
            if L not in coupling_lvals(la, lb):
                continue
            # The M = 0 Gaunt slice; the radial/aux factor kern_P is the
            # same for every (ma, mb) cell, so the sum over (ma, mb) of the
            # rank-1 updates g^2 (kern kern^T) collapses to a single update
            # weighted by the sum of squared Gaunt coefficients.
            g_mab = gaunt_table(la, lb, L)[:, :, L]
            gsq = float(np.sum(g_mab * g_mab))
            if gsq == 0.0:
                continue

            # Contraction-weighted radial column over P.
            n_ab = la + lb
            rad = np.zeros(nP, dtype=float)
            for ai, wi in zip(ea, wa):
                for aj, wj in zip(eb, wb):
                    alpha_ab = ai + aj
                    rj = np.fromiter(
                        (radial_integral(L, n_ab, L, alpha_ab, float(p)) for p in aP),
                        dtype=float, count=nP,
                    )
                    rad += (wi * wj) * rj
            kern_P = (4.0 * pi / (2 * L + 1)) * NP * rad

            W += gsq * np.outer(kern_P, kern_P)

    return W


def contract_aux(aos, per_L_alphas, contract_threshold=1.0e-4,
                 lindep_threshold=1.0e-7):
    """Build SVD-based general contractions per L per Lehtola, J. Chem.
    Theory Comput. 19, 6242 (2023)
    [https://doi.org/10.1021/acs.jctc.3c00670], eq 8, following ERKALE's
    ``basistool contractaux`` reference implementation.

    For each L the two-index Coulomb metric ``V = (P|Q)`` and the
    atomic-symmetry-reduced ``W`` block are formed over the selected
    primitives, then the primitives are Coulomb-normalized
    (``D = sqrt(diag V)``) so the work is done in the well-conditioned
    unit-diagonal metric ``S = D^{-1} V D^{-1}`` rather than the
    ill-conditioned raw metric.  ``S`` is symmetrically orthogonalized
    (dropping eigenvalues below ``lindep_threshold``), ``W`` is
    diagonalized in that orthonormal basis, and the eigenvectors with
    eigenvalue ``>= contract_threshold`` are kept and converted back to
    the overlap-normalized primitive convention.

    Parameters
    ----------
    aos : list of (l, alphas, weights)
        Contracted orbital AOs (from :func:`orbital_aos`) whose products
        define the three-index integrals to be fit.
    per_L_alphas : dict
        ``{L: [alpha, ...]}`` of selected aux exponents.
    contract_threshold : float
        Eigenvalue cutoff epsilon: contractions with eigenvalue
        ``lambda_i < epsilon`` are dropped.
    lindep_threshold : float
        Eigenvalue cutoff for the symmetric orthogonalization of the
        normalized Coulomb metric; directions below this are treated as
        linearly dependent and removed (ERKALE uses 1e-7).

    Returns
    -------
    dict
        ``{L: (exps, [gen1_coeffs, gen2_coeffs, ...])}``.  The
        coefficients are BSE-convention contraction coefficients of
        overlap-normalized primitives, in ERKALE's printing convention
        (``c = Wvec * sqrt(z)``).
    """
    out = {}
    for L, alphas in per_L_alphas.items():
        if not alphas:
            continue
        V = primitive_aux_metric(L, alphas)
        W = _W_block(aos, L, alphas)

        # Coulomb-normalize the primitives: switch to the unit-diagonal
        # metric S = D^{-1} V D^{-1} (D_i = sqrt((i|i))) and the
        # correspondingly normalized W.  This is the well-conditioned
        # basis the diagonalization must be carried out in.
        D = np.sqrt(np.diag(V))
        S = V / np.outer(D, D)
        Wn = W / np.outer(D, D)

        # Symmetric orthogonalization of the normalized metric, dropping
        # near-linearly-dependent directions.
        sval, svec = np.linalg.eigh(S)
        indep = sval >= lindep_threshold
        if not indep.any():
            indep[-1] = True
        X = svec[:, indep] * (sval[indep] ** -0.5)   # (nprim, nindep)

        # Diagonalize W in the orthonormal basis.
        Wsub = X.T @ Wn @ X
        lams, Y = np.linalg.eigh(Wsub)
        order = np.argsort(-lams)
        lams = lams[order]
        # Coefficients in the Coulomb-normalized primitive basis; these
        # are S-orthonormal, so each gives (A|A) = 1.
        Cnorm = X @ Y[:, order]

        # Per the paper, keep eigenvectors with lambda_i >= epsilon.
        # If everything is below threshold, keep the leading one so the
        # element still has an L block.
        keep_mask = lams >= contract_threshold
        if not keep_mask.any():
            keep_mask[0] = True
        keep = int(keep_mask.sum())

        # Convert Coulomb-normalized eigenvectors to the overlap-normalized
        # primitive convention printed by basis-set libraries, matching
        # ERKALE's basistool contractaux exactly: c = Wvec * sqrt(z).
        sqrt_z = np.sqrt(np.asarray(alphas, dtype=float))
        gens = [list(Cnorm[:, k] * sqrt_z) for k in range(keep)]
        out[L] = (list(alphas), gens)

    return out

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

  4. Convert the resulting contraction coefficients -- which are
     expressed in the Coulomb-normalized primitive basis, (a|a) = 1 --
     back to the overlap-normalized primitive convention used by basis
     set libraries, by dividing each coefficient by the Coulomb norm
     ``D_i = sqrt((i|i))``.  This is the exact analogue of the
     ``c <- c * sqrt(z)`` rescaling in ERKALE's ``basistool contractaux``
     (1/D is proportional to sqrt(z)); it guarantees the contracted
     functions satisfy (A|A) = 1 in the Coulomb metric.

This mirrors ERKALE's ``basistool contractaux`` reference implementation,
with the methodological improvement that atomic spherical symmetry is
used to reduce the W matrix to its m = 0 slice (Section 2.1 of the 2023
paper), which is not exploited in ERKALE.
"""

import numpy as np
from math import pi

from .gaunt import coupling_lvals, gaunt_table
from .radial import radial_integral, gto_norm, gto_norm_array
from .twoel import primitive_aux_metric


def _W_block(primitives, L, alphas_P):
    """Build the m=0 subblock of W at angular momentum L,

        W_PQ = sum_{mu nu m_mu m_nu} (mu nu | P)_{L 0} (mu nu | Q)_{L 0}.

    ``primitives`` is the list of orbital primitives
    ``[(l_ang, n_rad, alpha), ...]``; ``alphas_P`` are the aux exponents
    at this L (all standard primitives r^L e^{-alpha_P r^2}).

    Internally we factorise

        (mu nu | P)_{L, 0} = G(l_mu m_mu, l_nu m_nu, L, 0)
                            * (4 pi / (2 L + 1))
                            * N_mu N_nu N_P
                            * R_L(n_mu + n_nu, alpha_mu + alpha_nu; L, alpha_P)

    and sum over each orbital shell-pair as a single ``einsum``.
    """
    nP = len(alphas_P)
    if nP == 0:
        return np.zeros((0, 0), dtype=float)
    aP = np.asarray(alphas_P, dtype=float)
    NP = gto_norm_array(L, aP)

    # Pre-compute, per orbital shell-pair (l_a, n_a, alpha_a, l_b, n_b, alpha_b),
    # the (mu nu | P)_{L, 0} column as a function of P at this L:
    #
    #   col_{P,(ma,mb)} = sum_{(ma,mb)} G_{ma,mb,M=0} * R_L(..., alpha_P) * N's
    #
    # then accumulate ``col @ col.T`` into W.
    W = np.zeros((nP, nP), dtype=float)
    seen = set()  # (la, na, aa, lb, nb, ab) shell-pair keys

    for ia, (la, n_a, aa) in enumerate(primitives):
        Na = gto_norm(n_a, aa)
        for ib, (lb, n_b, ab) in enumerate(primitives):
            if L not in coupling_lvals(la, lb):
                continue
            # The orbital loops iterate every ordered (mu, nu) pair, which
            # is what eq 7 of the 2023 paper prescribes; no double-counting.
            Nb = gto_norm(n_b, ab)
            base = Na * Nb * (4.0 * pi / (2 * L + 1))

            # Gaunt vector at M = 0, indexed by (ma + la, mb + lb).
            g_mab = gaunt_table(la, lb, L)[:, :, L]  # the M = 0 slice
            if not g_mab.any():
                continue

            # Radial vector over P (depends on alpha_ab and alpha_P; cached).
            alpha_ab = aa + ab
            n_ab = n_a + n_b
            rad_P = np.fromiter(
                (radial_integral(L, n_ab, L, alpha_ab, float(p)) for p in aP),
                dtype=float, count=nP,
            )
            kern_P = base * NP * rad_P    # shape (nP,)

            # Sum over (ma, mb): contribute one rank-1 update per nonzero
            # Gaunt coefficient.  In atomic spherical symmetry the M=0 slice
            # has at most 2 l_min + 1 nonzero (ma, mb) cells, so this stays
            # cheap even without further vectorisation.
            for (ima, imb), g in np.ndenumerate(g_mab):
                if g == 0.0:
                    continue
                v = (g * kern_P)
                W += np.outer(v, v)

    return W


def contract_aux(primitives, per_L_alphas, contract_threshold=1.0e-4,
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
    primitives : list of (l, n, alpha)
        Orbital primitives (used to build the three-index ERIs).
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
        overlap-normalized primitives; each contracted function is
        normalized to ``(A|A) = 1`` in the Coulomb metric.
    """
    out = {}
    for L, alphas in per_L_alphas.items():
        if not alphas:
            continue
        V = primitive_aux_metric(L, alphas)
        W = _W_block(primitives, L, alphas)

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

        # Convert Coulomb-normalized coefficients to the overlap-normalized
        # primitive convention used by basis libraries: c <- c / D
        # (== c * sqrt(z) up to a per-L constant, cf. ERKALE basistool).
        gens = [list(Cnorm[:, k] / D) for k in range(keep)]
        out[L] = (list(alphas), gens)

    return out

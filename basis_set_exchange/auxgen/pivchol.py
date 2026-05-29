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
Pivoted Cholesky decomposition with a drop tolerance.

Given a symmetric positive (semi-)definite matrix A, return the list of
pivot indices selected by the greedy diagonal-maximizing pivoted
Cholesky algorithm and the corresponding lower-triangular Cholesky
factor.  The decomposition terminates when the largest residual
diagonal falls below the absolute drop tolerance ``tol`` (matching the
convention of ERKALE's ``ERIchol::fill`` and
``cholesky_pick_exponents``; for normalized unit-diagonal metrics this
also equals the relative-to-initial-max tolerance).

A single inner kernel is shared between the plain pivoted Cholesky
(:func:`pivoted_cholesky`) and the shell-pair-driven variant
(:func:`block_pivoted_cholesky`).  They differ only in pivot
*selection*: the plain version picks the index with the largest
residual diagonal at every step; the block version, after each such
greedy pick, additionally processes every remaining member of the
pivot's block before the next greedy search.  This matches the
ERKALE convention behind Lehtola, J. Chem. Theory Comput. 17, 6886
(2021) [https://doi.org/10.1021/acs.jctc.1c00607]: an auxiliary
candidate is always added as the complete shell-pair its pivot
belongs to.
"""

import numpy as np


def _pivoted_cholesky_core(A, tol, next_pivot, max_rank=None):
    """Inner kernel: run pivoted Cholesky on ``A`` with drop tolerance
    ``tol`` until ``next_pivot(diag, done)`` returns ``None``.

    Parameters
    ----------
    A : numpy.ndarray, shape (n, n)
        Symmetric positive (semi-)definite matrix.
    tol : float
        Absolute residual-diagonal drop tolerance.
    next_pivot : callable
        Called with ``(diag, done)`` to yield successive pivot indices.
        ``done`` is a boolean mask of already-processed indices; the
        callback may inspect the up-to-date residual diagonal and
        return either an ``int`` index in ``range(n)`` (not yet
        ``done``) or ``None`` to terminate.
    max_rank : int, optional
        Hard cap on the number of pivots.

    Returns
    -------
    pivots, L : (list of int, numpy.ndarray)
        Selected pivot indices in selection order, and the Cholesky
        factor ``L`` (shape ``(n, len(pivots))``) such that
        ``A ~= L @ L.T``.
    """
    n = A.shape[0]
    cap = n if max_rank is None else min(max_rank, n)

    diag = np.diag(A).astype(float).copy()
    L_factor = np.empty((n, cap), dtype=float)
    done = np.zeros(n, dtype=bool)
    pivots = []
    m = 0

    while m < cap:
        i = next_pivot(diag, done)
        if i is None:
            break

        # Column update via a single matvec against the already-built block:
        # col_k = A[:, i] - L[:, :m] @ L[i, :m].
        if m > 0:
            col = A[:, i] - L_factor[:, :m] @ L_factor[i, :m]
        else:
            col = A[:, i].astype(float).copy()
        piv_val = diag[i]
        if piv_val <= 0.0:
            col[:] = 0.0
        else:
            col /= np.sqrt(piv_val)

        diag -= col * col
        diag[i] = 0.0
        done[i] = True
        L_factor[:, m] = col
        m += 1
        pivots.append(i)

    if m == 0:
        return pivots, np.zeros((n, 0), dtype=float)
    return pivots, L_factor[:, :m].copy()


# ---------------------------------------------------------------------------
# Pivot-selection strategies
# ---------------------------------------------------------------------------

def _make_greedy_picker(tol):
    """Pick the index with the largest residual diagonal among the
    unprocessed indices; stop when it falls at or below ``tol``.
    """
    def pick(diag, done):
        masked = np.where(done, -np.inf, diag)
        i = int(np.argmax(masked))
        if masked[i] <= tol or diag[i] <= 0.0:
            return None
        return i
    return pick


def _make_block_picker(tol, block_members, block_of):
    """ERKALE shell-pair convention.

    The first call inside a new block returns the standard greedy max
    pivot.  Subsequent calls return the remaining members of that
    pivot's block, in their original order, regardless of their
    residual-diagonal value.  Once the block is exhausted, the next
    call resumes the greedy search.
    """
    greedy = _make_greedy_picker(tol)
    pending = []   # remaining indices from the current block

    def pick(diag, done):
        # Drain the current block first.
        while pending:
            j = pending.pop(0)
            if done[j]:
                continue
            if diag[j] <= 0.0:
                # Numerical noise -- mark done and skip without factoring.
                done[j] = True
                continue
            return j

        i = greedy(diag, done)
        if i is None:
            return None
        # Queue the other members of this block.
        pending.extend(j for j in block_members[block_of[i]] if j != i)
        return i

    return pick


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def pivoted_cholesky(A, tol=1.0e-6, max_rank=None):
    """Pivoted Cholesky with drop tolerance.

    Stops when the maximum residual diagonal is at or below ``tol``.

    Returns
    -------
    pivots : list of int
        Indices of the selected pivots, in the order they were picked.
    L : numpy.ndarray, shape (n, len(pivots))
        Lower Cholesky factor so that ``A ~= L @ L.T``.
    """
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    if n == 0:
        return [], np.zeros((0, 0), dtype=float)
    assert A.shape == (n, n)
    if np.diag(A).max() <= 0.0:
        return [], np.zeros((n, 0), dtype=float)

    return _pivoted_cholesky_core(A, tol, _make_greedy_picker(tol), max_rank=max_rank)


def block_pivoted_cholesky(A, block_of, tol=1.0e-6):
    """Shell-pair-driven pivoted Cholesky (ERKALE convention).

    At each step:

      1. The index with the largest residual diagonal is selected
         exactly as in :func:`pivoted_cholesky`.
      2. That index is processed as a pivot.
      3. Every other index that shares the same block (``block_of[i]``)
         is then processed as a pivot before the next greedy search,
         regardless of its own residual-diagonal value.

    Parameters
    ----------
    A : array_like, shape (n, n)
        Symmetric positive (semi-)definite matrix.
    block_of : sequence of length n
        ``block_of[i]`` is a hashable identifier for the block
        (typically the orbital shell-pair) that index ``i`` belongs
        to.  Two indices in the same block are guaranteed to be
        selected together.
    tol : float
        Absolute drop tolerance on the residual diagonal.

    Returns
    -------
    pivots, L : (list of int, numpy.ndarray)
        See :func:`pivoted_cholesky`.  Members of the same block are
        listed contiguously in ``pivots``.
    """
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    if n == 0:
        return [], np.zeros((0, 0), dtype=float)
    assert A.shape == (n, n)
    assert len(block_of) == n
    if np.diag(A).max() <= 0.0:
        return [], np.zeros((n, 0), dtype=float)

    block_members = {}
    for i, b in enumerate(block_of):
        block_members.setdefault(b, []).append(i)

    return _pivoted_cholesky_core(A, tol,
                                  _make_block_picker(tol, block_members, block_of))

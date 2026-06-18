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

# Tests for basis_set_exchange.auxgen.

import math

import pytest

numpy = pytest.importorskip('numpy')

from basis_set_exchange import get_basis, write_formatted_basis_str
from basis_set_exchange.auxgen.gaunt import real_gaunt, coupling_lvals
from basis_set_exchange.auxgen.radial import (
    radial_integral, alpha_eff,
)
from basis_set_exchange.auxgen.twoel import (
    primitive_eri, primitive_aux_metric, normalized_metric,
)
from basis_set_exchange.auxgen.pivchol import pivoted_cholesky
from basis_set_exchange.auxgen import generate_auxiliary_basis


# ---------------------------------------------------------------------------
# Gaunt coefficients
# ---------------------------------------------------------------------------

def test_real_gaunt_normalization():
    # <S_00 S_00 S_00> = (1/sqrt(4pi))^3 * 4pi = 1/(2 sqrt(pi))
    assert real_gaunt(0, 0, 0, 0, 0, 0) == pytest.approx(1.0 / (2.0 * math.sqrt(math.pi)))


def test_real_gaunt_selection_rules():
    # Parity violation
    assert real_gaunt(1, 0, 1, 0, 1, 0) == 0.0
    # Triangle violation (1 + 1 = 2 > 0, but 1 + 1 - 4 = -2 invalid)
    assert real_gaunt(1, 0, 1, 0, 4, 0) == 0.0


def test_coupling_lvals_pp():
    # Two p functions couple to L = 0, 2 (parity)
    assert coupling_lvals(1, 1) == (0, 2)
    assert coupling_lvals(2, 2) == (0, 2, 4)
    assert coupling_lvals(1, 2) == (1, 3)


# ---------------------------------------------------------------------------
# Radial integrals
# ---------------------------------------------------------------------------

def test_radial_selection_rules():
    # L > LA
    assert radial_integral(1, 0, 0, 0.5, 1.0) == 0.0
    # parity
    assert radial_integral(0, 0, 1, 0.5, 1.0) == 0.0
    assert radial_integral(0, 1, 0, 0.5, 1.0) == 0.0


def test_radial_ss_against_analytic():
    # (s_a s_a | s_b s_b) = 2 sqrt(2 a b / (pi (a + b)))
    for a, b in [(0.5, 1.5), (1.0, 1.0), (0.01, 100.0)]:
        # primitive_eri signature: (la, na, ma, alpha_a, lb, nb, mb, alpha_b, ...)
        val = primitive_eri(0, 0, 0, a, 0, 0, 0, a,
                            0, 0, 0, b, 0, 0, 0, b)
        expected = 2.0 * math.sqrt(2 * a * b / (math.pi * (a + b)))
        assert val == pytest.approx(expected, rel=1e-12)


def test_radial_closed_form_ss():
    # R_0(a, 0; b, 0) = sqrt(pi) / (8 a b sqrt(a + b))
    for a, b in [(1.0, 1.0), (0.5, 1.5), (0.01, 100.0)]:
        v = radial_integral(0, 0, 0, a, b)
        expected = math.sqrt(math.pi) / (8.0 * a * b * math.sqrt(a + b))
        assert v == pytest.approx(expected, rel=1e-12)


def test_radial_symmetric_tuple():
    # R_L(L, L) symmetric under a <-> b
    assert radial_integral(2, 2, 2, 0.3, 1.7) == pytest.approx(
        radial_integral(2, 2, 2, 1.7, 0.3), rel=1e-13)
    assert radial_integral(4, 4, 4, 0.2, 3.5) == pytest.approx(
        radial_integral(4, 4, 4, 3.5, 0.2), rel=1e-13)


# ---------------------------------------------------------------------------
# Higher-L ERI validation via independent numerical quadrature.
# ---------------------------------------------------------------------------

def _radial_by_quadrature(L, na, nb, a, b):
    """Independent computation of R_L(a, n_a; b, n_b) by scipy
    double-quadrature.  Slow -- used only for validation.
    """
    scipy_integrate = pytest.importorskip('scipy.integrate')
    import math as _m

    def integrand(r2, r1):
        if r1 == 0.0 or r2 == 0.0:
            return 0.0
        rlt = min(r1, r2); rgt = max(r1, r2)
        mp = (rlt**L) / (rgt**(L + 1))
        return r1**(na + 2) * r2**(nb + 2) * _m.exp(-a * r1**2 - b * r2**2) * mp

    # Truncate the outer Gaussians at roughly 8 / sqrt(min(a, b)).
    rmax = 8.0 / _m.sqrt(min(a, b))
    val, _err = scipy_integrate.dblquad(
        integrand, 0.0, rmax, 0.0, rmax,
        epsabs=1e-12, epsrel=1e-10)
    return val


@pytest.mark.parametrize("L,na,nb,a,b", [
    (0, 0, 0, 0.7, 1.3),
    (0, 2, 2, 0.7, 1.3),
    (2, 2, 2, 0.7, 1.3),
    (0, 4, 4, 0.7, 1.3),
    (2, 4, 4, 0.7, 1.3),
    (4, 4, 4, 0.7, 1.3),
    (0, 2, 4, 0.5, 2.0),
    (2, 2, 4, 0.5, 2.0),
])
def test_radial_pitzer_vs_quadrature(L, na, nb, a, b):
    closed = radial_integral(L, na, nb, a, b)
    numeric = _radial_by_quadrature(L, na, nb, a, b)
    assert closed == pytest.approx(numeric, rel=1e-6)


def test_eri_full_tensor_vs_pyscf_spd():
    """End-to-end angular validation: compare every (ab|cd) integral
    over an s/p/d primitive set against PySCF's libcint, which uses
    real spherical harmonics with the m ordering (px, py, pz) = (+1,
    -1, 0) for l=1 and (-2, -1, 0, +1, +2) for l>=2.
    """
    pytest.importorskip('pyscf')
    from pyscf import gto

    mol = gto.Mole()
    mol.atom = "He 0 0 0"
    mol.basis = {'He': [[0, [0.3, 1.0]], [0, [1.7, 1.0]],
                        [1, [1.1, 1.0]], [2, [0.8, 1.0]]]}
    mol.unit = 'Bohr'
    mol.cart = False
    mol.build()
    eri = mol.intor('int2e_sph')

    ao_info = [
        (0, 0, 0.3),
        (0, 0, 1.7),
        (1, +1, 1.1), (1, -1, 1.1), (1, 0, 1.1),
        (2, -2, 0.8), (2, -1, 0.8), (2, 0, 0.8), (2, +1, 0.8), (2, +2, 0.8),
    ]
    max_err = 0.0
    for i, (la, ma, aa) in enumerate(ao_info):
        for j, (lb, mb, ab) in enumerate(ao_info):
            for k, (lc, mc, ac) in enumerate(ao_info):
                for l_, (ld, md, ad) in enumerate(ao_info):
                    v_me = primitive_eri(la, la, ma, aa, lb, lb, mb, ab,
                                         lc, lc, mc, ac, ld, ld, md, ad)
                    max_err = max(max_err, abs(v_me - eri[i, j, k, l_]))
    assert max_err < 1e-12


def test_eri_index_symmetries_pp_pp():
    # (ab|cd) = (ba|cd) = (ab|dc) = (cd|ab) for one-center spherical Gaussians.
    a, b, c, d = 0.5, 1.5, 0.8, 2.7
    args_abcd = (1, 1, 0, a, 1, 1, 0, b, 1, 1, 0, c, 1, 1, 0, d)
    v_abcd = primitive_eri(*args_abcd)
    # (ba|cd) -- swap first pair
    v_bacd = primitive_eri(1, 1, 0, b, 1, 1, 0, a, 1, 1, 0, c, 1, 1, 0, d)
    # (ab|dc)
    v_abdc = primitive_eri(1, 1, 0, a, 1, 1, 0, b, 1, 1, 0, d, 1, 1, 0, c)
    # (cd|ab)
    v_cdab = primitive_eri(1, 1, 0, c, 1, 1, 0, d, 1, 1, 0, a, 1, 1, 0, b)
    assert v_abcd == pytest.approx(v_bacd, rel=1e-13)
    assert v_abcd == pytest.approx(v_abdc, rel=1e-13)
    assert v_abcd == pytest.approx(v_cdab, rel=1e-13)


def test_eri_index_symmetries_dd_dd_mixed_m():
    # Same symmetries for d functions with non-trivial M dependence.
    a, b = 0.7, 1.6
    # Pick two different m's to mix in the Gaunt sum
    v1 = primitive_eri(2, 2, 1, a, 2, 2, -1, b, 2, 2, 1, a, 2, 2, -1, b)
    v2 = primitive_eri(2, 2, -1, b, 2, 2, 1, a, 2, 2, -1, b, 2, 2, 1, a)
    assert v1 == pytest.approx(v2, rel=1e-13)


def test_eri_tensor_psd():
    # (mu nu | rho sigma) viewed as a metric on m-resolved pair indices
    # must be positive semi-definite.  Use a small primitive set.
    from basis_set_exchange.auxgen.products import primitive_product_pairs
    from basis_set_exchange.auxgen.twoel import product_metric
    primitives = [(0, 0, 1.0), (1, 1, 0.5)]
    pairs = primitive_product_pairs(primitives)
    M = product_metric(pairs)
    eigs = numpy.linalg.eigvalsh(M)
    # Allow tiny numerical negatives.
    assert eigs[0] > -1e-10
    assert M.shape[0] == len(pairs)


# ---------------------------------------------------------------------------
# Cartesian / spherical equivalence and contamination handling
# ---------------------------------------------------------------------------

def test_cartesian_shell_expands_to_lower_l():
    from basis_set_exchange.auxgen.products import decontract_primitives
    # A single d cartesian shell at alpha=1.0 contributes (l=2, n=2, 1.0)
    # AND (l=0, n=2, 1.0) primitives.
    eb = {
        'electron_shells': [
            {
                'function_type': 'gto_cartesian',
                'region': '',
                'angular_momentum': [2],
                'exponents': ['1.0'],
                'coefficients': [['1.0']],
            }
        ]
    }
    prims = decontract_primitives(eb)
    assert (2, 2, 1.0) in prims
    assert (0, 2, 1.0) in prims  # the cartesian-d s contamination
    # And that's it.
    assert len(prims) == 2


def test_spherical_shell_no_contamination():
    from basis_set_exchange.auxgen.products import decontract_primitives
    eb = {
        'electron_shells': [
            {
                'function_type': 'gto_spherical',
                'region': '',
                'angular_momentum': [2],
                'exponents': ['1.0'],
                'coefficients': [['1.0']],
            }
        ]
    }
    prims = decontract_primitives(eb)
    assert prims == [(2, 2, 1.0)]


def test_ecp_shells_ignored():
    # ECP entries live under ``ecp_potentials`` and must be skipped.
    from basis_set_exchange.auxgen.products import decontract_primitives
    eb = {
        'electron_shells': [
            {'function_type': 'gto_spherical', 'region': '',
             'angular_momentum': [0], 'exponents': ['1.0'],
             'coefficients': [['1.0']]},
        ],
        'ecp_potentials': [
            {'ecp_type': 'scalar_ecp', 'angular_momentum': [0],
             'r_exponents': [2], 'gaussian_exponents': ['5.0'],
             'coefficients': [['1.0']]},
        ],
        'ecp_electrons': 10,
    }
    prims = decontract_primitives(eb)
    assert prims == [(0, 0, 1.0)]


def test_alpha_eff_diagonal():
    # For L = l_rad: alpha_eff = alpha_rad
    assert alpha_eff(0, 0, 1.0) == pytest.approx(1.0)
    assert alpha_eff(4, 4, 0.5) == pytest.approx(0.5)
    # For L < l_rad: alpha_eff < alpha_rad (candidate is more diffuse)
    assert alpha_eff(0, 4, 1.0) < 1.0


# ---------------------------------------------------------------------------
# Aux primitive metric is positive definite
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('L', [0, 1, 2, 3, 4])
def test_primitive_aux_metric_pd(L):
    M = primitive_aux_metric(L, [0.1, 0.3, 1.0, 3.0, 10.0])
    eigs = numpy.linalg.eigvalsh(M)
    assert (eigs > 0).all()


# ---------------------------------------------------------------------------
# Candidate metric: S_ii == 1, S PD
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('L', [0, 1, 2, 3])
def test_normalized_metric_unit_diagonal_psd(L):
    S = normalized_metric(L, [0.1, 0.3, 1.0, 3.0, 10.0])
    assert numpy.allclose(numpy.diag(S), 1.0)
    eigs = numpy.linalg.eigvalsh(S)
    assert (eigs > 0).all()


# ---------------------------------------------------------------------------
# Pivoted Cholesky
# ---------------------------------------------------------------------------

def test_pivoted_cholesky_rank_revealing():
    rng = numpy.random.default_rng(0)
    X = rng.standard_normal((8, 4))
    A = X @ X.T
    pivots, L = pivoted_cholesky(A, tol=1e-10)
    assert len(pivots) == 4
    assert numpy.linalg.norm(A - L @ L.T) < 1e-10


def test_pivoted_cholesky_psd_perturbation():
    rng = numpy.random.default_rng(0)
    X = rng.standard_normal((6, 3))
    A = X @ X.T + 1e-2 * numpy.eye(6)
    pivots, L = pivoted_cholesky(A, tol=1e-8)
    # Full rank
    assert len(pivots) == 6
    assert numpy.linalg.norm(A - L @ L.T) < 1e-10


# ---------------------------------------------------------------------------
# End-to-end pipeline
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('scheme', ['basic', 'reduced'])
def test_end_to_end_H_cc_pvdz(scheme):
    b = get_basis('cc-pVDZ', elements=[1])
    aux = generate_auxiliary_basis(b, threshold=1e-7, scheme=scheme,
                                   contract=False, prune_lmax=False)
    shells = aux['elements']['1']['electron_shells']
    assert len(shells) >= 5
    # All shells are spherical Gaussians with one primitive each
    for s in shells:
        assert s['function_type'] == 'gto_spherical'
        assert len(s['exponents']) == 1


def test_end_to_end_contracted():
    b = get_basis('cc-pVDZ', elements=[6])
    aux = generate_auxiliary_basis(
        b, threshold=1e-7, scheme='reduced',
        contract=True, contract_threshold=1e-4)
    shells = aux['elements']['6']['electron_shells']
    # One shell per L
    L_set = set(s['angular_momentum'][0] for s in shells)
    assert len(L_set) == len(shells)
    # General-contracted: at least one shell has > 1 generalized contraction
    assert any(len(s['coefficients']) > 1 for s in shells)


def test_random_shuffles_no_worse_than_presort():
    # Lehtola 2021 Note Added in Proof: trying random orderings can give
    # a more compact decomposition.  We require only that the random
    # variant never produces *more* functions than the deterministic
    # presort, for any element / scheme combination.
    b = get_basis('cc-pVDZ', elements=[6])
    det = generate_auxiliary_basis(b, threshold=1e-7, scheme='basic',
                                    n_random=0)
    rnd = generate_auxiliary_basis(b, threshold=1e-7, scheme='basic',
                                    n_random=32, seed=0)
    nd = len(det['elements']['6']['electron_shells'])
    nr = len(rnd['elements']['6']['electron_shells'])
    assert nr <= nd


def test_random_seed_reproducibility():
    b = get_basis('cc-pVDZ', elements=[6])
    a1 = generate_auxiliary_basis(b, threshold=1e-7, scheme='basic',
                                   n_random=8, seed=42)
    a2 = generate_auxiliary_basis(b, threshold=1e-7, scheme='basic',
                                   n_random=8, seed=42)
    e1 = a1['elements']['6']['electron_shells']
    e2 = a2['elements']['6']['electron_shells']
    assert len(e1) == len(e2)
    for s1, s2 in zip(e1, e2):
        assert s1['angular_momentum'] == s2['angular_momentum']
        assert s1['exponents'] == s2['exponents']


# ---------------------------------------------------------------------------
# Cholesky selector properties
# ---------------------------------------------------------------------------

def test_cholesky_subset_of_candidate_pool():
    """The pivoted-Cholesky selection returns a subset of the original
    pool (no new exponents are invented); never empty for a non-empty
    input."""
    from basis_set_exchange.auxgen.products import (
        decontract_primitives, candidate_pool_from_primitives,
    )
    b = get_basis('cc-pVDZ', elements=[6])
    eb = b['elements']['6']
    primitives = decontract_primitives(eb)
    pool = candidate_pool_from_primitives(primitives)

    aux = generate_auxiliary_basis(b, elements=[6], threshold=1.0e-7,
                                    scheme='basic', n_random=0)
    by_L = {}
    for s in aux['elements']['6']['electron_shells']:
        by_L.setdefault(s['angular_momentum'][0], []).append(float(s['exponents'][0]))
    for L, kept in by_L.items():
        assert len(kept) > 0
        pool_set = {round(a, 10) for a in pool.get(L, [])}
        assert all(round(a, 10) in pool_set for a in kept)


def test_tighter_threshold_keeps_more():
    """Lowering the drop threshold can only retain more primitives."""
    b = get_basis('cc-pVDZ', elements=[6])
    a_loose = generate_auxiliary_basis(b, threshold=1.0e-3,
                                        scheme='basic', n_random=0)
    a_tight = generate_auxiliary_basis(b, threshold=1.0e-8,
                                        scheme='basic', n_random=0)
    nl = len(a_loose['elements']['6']['electron_shells'])
    nt = len(a_tight['elements']['6']['electron_shells'])
    assert nt >= nl


def test_end_to_end_lmax_pruning():
    b = get_basis('cc-pVDZ', elements=[6])
    aux = generate_auxiliary_basis(b, threshold=1e-7, scheme='reduced',
                                    prune_lmax=True, linc=1)
    shells = aux['elements']['6']['electron_shells']
    # Carbon: lmax_occ = 1, lmax_obs = 2 (cc-pVDZ d), linc = 1 ->
    # l_keep = max(2*1, 1+2+1) = 4.  No shell should exceed L = 4.
    for s in shells:
        assert s['angular_momentum'][0] <= 4


# ---------------------------------------------------------------------------
# Contraction: normalization and accuracy
# ---------------------------------------------------------------------------

def test_contracted_coefficients_match_erkale_convention():
    """The output coefficient convention is ERKALE's ``c = Wvec * sqrt(z)``.
    All contractions at a given L share the per-L Coulomb norm scale
    ``(A|A) = k_L^2`` where ``k_L^2 = z_i * V_ii`` is constant in z (since
    (i|i) ~ 1/z for an overlap-normalized primitive)."""
    from basis_set_exchange.auxgen.twoel import primitive_aux_metric

    b = get_basis('cc-pVTZ', elements=[8])
    aux = generate_auxiliary_basis(b, elements=[8], threshold=1e-7,
                                   contract=True, contract_threshold=1e-5,
                                   prune_lmax=False)
    for s in aux['elements']['8']['electron_shells']:
        L = s['angular_momentum'][0]
        exps = [float(e) for e in s['exponents']]
        V = primitive_aux_metric(L, exps)
        k2 = float(exps[0] * V[0, 0])
        for coeff in s['coefficients']:
            c = numpy.array([float(x) for x in coeff])
            aa = c @ V @ c
            assert abs(aa - k2) / k2 < 1e-6, \
                f"L={L}: (A|A)={aa}, expected k_L^2={k2}"


@pytest.mark.parametrize('size,eps,linc', [
    ('verylarge', 1e-6, 1),
    ('large', 1e-5, 1),
    ('small', 1e-4, 0),
])
def test_size_presets_match_paper(size, eps, linc):
    """The size presets must reproduce the (epsilon, l_inc) pairs of the
    2023 paper and force contraction + lmax pruning on."""
    b = get_basis('cc-pVTZ', elements=[8])
    aux_preset = generate_auxiliary_basis(b, elements=[8], size=size)
    aux_manual = generate_auxiliary_basis(b, elements=[8], contract=True,
                                          contract_threshold=eps,
                                          prune_lmax=True, linc=linc)
    sp = aux_preset['elements']['8']['electron_shells']
    sm = aux_manual['elements']['8']['electron_shells']
    assert len(sp) == len(sm)
    for a, c in zip(sp, sm):
        assert a['angular_momentum'] == c['angular_momentum']
        assert a['exponents'] == c['exponents']
        assert a['coefficients'] == c['coefficients']


def test_size_presets_ordering():
    """small (linc=0) is no larger than large/verylarge (linc=1)."""
    b = get_basis('cc-pVTZ', elements=[8])
    n = {}
    for size in ('small', 'large', 'verylarge'):
        aux = generate_auxiliary_basis(b, elements=[8], size=size)
        sh = aux['elements']['8']['electron_shells']
        n[size] = sum(2 * s['angular_momentum'][0] + 1 for s in sh)
    assert n['small'] <= n['large'] <= n['verylarge']


def test_df_energy_contracted_matches_primitive():
    """A density-fitted atomic SCF with the contracted auxiliary basis
    must reproduce the energy of the tight-threshold *primitive*
    auxiliary basis to high accuracy (validates that the contraction is
    norm-correct and information-preserving)."""
    pytest.importorskip('pyscf')
    from pyscf import gto, scf

    elem = 'Ne'
    b = get_basis('cc-pVDZ', elements=[elem])
    aux_prim = generate_auxiliary_basis(b, threshold=1e-8, contract=False,
                                        prune_lmax=False)
    aux_contr = generate_auxiliary_basis(b, threshold=1e-8, contract=True,
                                         contract_threshold=1e-5, prune_lmax=False)

    def to_pyscf(aux):
        aux = dict(aux)
        aux.setdefault('function_types', ['gto_spherical'])
        aux.setdefault('names', ['auxgen'])
        return gto.basis.parse(write_formatted_basis_str(aux, 'nwchem'))

    mol = gto.M(atom=f'{elem} 0 0 0', basis='cc-pvdz', spin=0, verbose=0)
    e_prim = scf.RHF(mol).density_fit(auxbasis={elem: to_pyscf(aux_prim)}).kernel()
    e_contr = scf.RHF(mol).density_fit(auxbasis={elem: to_pyscf(aux_contr)}).kernel()
    assert abs(e_prim - e_contr) < 1e-5, \
        f"DF-HF energy differs by {abs(e_prim - e_contr):.3e} Hartree"


# ---------------------------------------------------------------------------
# Orbital-product -> auxiliary-primitive mapping
# ---------------------------------------------------------------------------

def test_alpha_eff_mappings_identity_at_nrad_equals_L():
    """Both mappings leave a standard primitive (n_rad == L) unchanged."""
    from basis_set_exchange.auxgen.radial import alpha_eff
    for L in range(4):
        for m in ('moment', 'selfrepulsion'):
            assert abs(alpha_eff(L, L, 2.5, m) - 2.5) < 1e-12


def test_alpha_eff_selfrepulsion_matches_self_energy():
    """The 'selfrepulsion' mapping must give a standard r^L primitive with
    the same Coulomb self-energy (i|i) as the (n_rad, alpha_rad)
    candidate."""
    from math import pi
    from basis_set_exchange.auxgen.radial import alpha_eff, gto_norm, radial_integral

    def self_energy(L, n, a):
        return gto_norm(n, a)**2 * (4 * pi / (2 * L + 1)) * radial_integral(L, n, n, a, a)

    for L, n_rad, a_rad in [(0, 2, 1.3), (1, 3, 0.7), (2, 4, 2.1), (0, 4, 0.5)]:
        ae = alpha_eff(L, n_rad, a_rad, 'selfrepulsion')
        assert abs(self_energy(L, n_rad, a_rad) - self_energy(L, L, ae)) < 1e-10 * self_energy(L, n_rad, a_rad)


def test_mapping_default_is_moment():
    """The default mapping is 'moment'; selecting it explicitly is a no-op."""
    b = get_basis('cc-pVDZ', elements=[8])
    a_default = generate_auxiliary_basis(b, elements=[8])
    a_moment = generate_auxiliary_basis(b, elements=[8], mapping='moment')
    assert a_default == a_moment
    # 'selfrepulsion' is accepted and produces a valid basis
    a_sr = generate_auxiliary_basis(b, elements=[8], mapping='selfrepulsion')
    assert len(a_sr['elements']['8']['electron_shells']) > 0


# ---------------------------------------------------------------------------
# Single-primitive replacement of contracted orbital functions (selection)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('mapping', ['moment', 'selfrepulsion'])
def test_match_single_primitive_identity_and_within_range(mapping):
    from basis_set_exchange.auxgen.products import _COLLAPSE_MATCHERS
    matcher = _COLLAPSE_MATCHERS[mapping]
    # A single-term "contraction" must recover its own exponent.
    assert abs(matcher(0, [2.5], [1.0]) - 2.5) < 1e-10
    assert abs(matcher(2, [1.7], [1.0]) - 1.7) < 1e-10
    # A two-term contraction maps to an exponent strictly between them.
    beta = matcher(0, [1.0, 16.0], [0.6, 0.6])
    assert 1.0 < beta < 16.0


def test_match_single_primitive_moment_preserves_r_expectation():
    """The 'moment' matcher must give a single primitive whose radial
    expectation value <r> equals that of the contraction."""
    from math import gamma
    from basis_set_exchange.auxgen.products import _match_single_primitive_moment
    from basis_set_exchange.auxgen.radial import gto_norm_array
    L = 2
    exps = [4.0, 1.5, 0.5]; c = [0.3, 0.5, 0.4]
    # Renormalize c so that the contraction is overlap-normalized.
    a = numpy.asarray(exps); cc = numpy.asarray(c); N = gto_norm_array(L, a)
    Sab = a[:, None] + a[None, :]
    ovl_chi = float(0.5 * gamma(L + 1.5) *
                    numpy.sum(cc[:, None]*cc[None, :] * N[:, None]*N[None, :] / Sab**(L + 1.5)))
    cc /= numpy.sqrt(ovl_chi)
    beta = _match_single_primitive_moment(L, exps, cc.tolist())
    r_chi = 0.5 * gamma(L + 2) * float(numpy.sum(
        cc[:, None]*cc[None, :] * N[:, None]*N[None, :] / Sab**(L + 2)))
    r_g = gamma(L + 2) / (gamma(L + 1.5) * numpy.sqrt(2 * beta))
    assert abs(r_chi - r_g) / abs(r_chi) < 1e-10


def test_match_single_primitive_selfrepulsion_preserves_coulomb_self_energy():
    """The 'selfrepulsion' matcher must give a single primitive whose
    orbital Coulomb self-energy (chi chi | chi chi) equals that of the
    contraction (four-index ERI of the electron density)."""
    from basis_set_exchange.auxgen.products import _match_single_primitive_selfrepulsion
    from basis_set_exchange.auxgen.twoel import primitive_eri
    L = 1
    exps = [3.0, 1.0, 0.4]; c = [0.4, 0.5, 0.2]
    n = len(exps)
    chichi = 0.0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for m in range(n):
                    chichi += c[i]*c[j]*c[k]*c[m] * primitive_eri(
                        L,L,0,exps[i], L,L,0,exps[j],
                        L,L,0,exps[k], L,L,0,exps[m])
    beta = _match_single_primitive_selfrepulsion(L, exps, c)
    gg = primitive_eri(L,L,0,beta, L,L,0,beta, L,L,0,beta, L,L,0,beta)
    assert abs(chichi - gg) / abs(chichi) < 1e-10


@pytest.mark.parametrize('mapping', ['moment', 'selfrepulsion'])
def test_collapse_contractions_one_primitive_per_contracted_function(mapping):
    from basis_set_exchange.auxgen.products import (
        decontract_primitives, decontract_primitives_single,
    )
    b = get_basis('cc-pVDZ', elements=[6])  # (9s,4p,1d) -> [3s,2p,1d]
    eb = b['elements']['6']
    single = decontract_primitives_single(eb, mapping=mapping)
    from collections import Counter
    lc = Counter(l for l, _n, _a in single)
    # One effective primitive per contracted AO: 3s, 2p, 1d.
    assert lc[0] == 3 and lc[1] == 2 and lc[2] == 1
    # Strictly fewer than full decontraction.
    assert len(single) < len(decontract_primitives(eb))
    # Every matched exponent lies within the parent shell's exponent span.
    span = {}
    for sh in eb['electron_shells']:
        L = sh['angular_momentum'][0]
        es = [float(e) for e in sh['exponents']]
        span.setdefault(L, []).extend(es)
    for l, _n, a in single:
        assert min(span[l]) <= a <= max(span[l])


def test_collapse_contractions_default_off():
    b = get_basis('cc-pVDZ', elements=[6])
    a_default = generate_auxiliary_basis(b, elements=[6])
    a_off = generate_auxiliary_basis(b, elements=[6], collapse_contractions=False)
    assert a_default == a_off
    for mode in ('moment', 'selfrepulsion'):
        a_on = generate_auxiliary_basis(b, elements=[6], collapse_contractions=mode)
        assert len(a_on['elements']['6']['electron_shells']) > 0


# ---------------------------------------------------------------------------
# Generated aux basis quality (diagonal RI error)
# ---------------------------------------------------------------------------

def _diag_ri_error_primitive_aux(orbital_elem, aux_elem):
    """For a *primitive* aux basis (one primitive per kept candidate, no
    SVD contraction), compute the diagonal RI error

        sum_{rs} [(rs|rs)_exact - (rs|rs)_RI]

    summed over m-resolved orbital primitive product pairs ``(r, s)``.

    Uses :func:`twoel.orbital_aux_projection` block-per-L to assemble
    the three-index J matrix, the two-index V metric, and the
    per-row exact value ``(rs|rs)_L,M``; the RI fit is
    ``diag(J V^{-1} J^T)``.
    """
    from basis_set_exchange.auxgen.products import decontract_primitives
    from basis_set_exchange.auxgen.twoel import orbital_aux_projection
    from basis_set_exchange.auxgen.gaunt import coupling_lvals, gaunt_table
    from basis_set_exchange.auxgen.radial import radial_integral, gto_norm
    from math import pi

    primitives = decontract_primitives(orbital_elem)

    # Aux primitives per L (each electron_shell is a single-primitive
    # shell when the aux basis was generated with contract=False).
    per_L = {}
    for s in aux_elem['electron_shells']:
        L = s['angular_momentum'][0]
        assert len(s['coefficients']) == 1, \
            "diagonal RI helper expects a primitive (uncontracted) aux basis"
        for e in s['exponents']:
            per_L.setdefault(L, []).append(float(e))

    err = 0.0
    for L, alphas in per_L.items():
        V, J = orbital_aux_projection(L, primitives, alphas)
        if J.size == 0:
            continue
        Vinv_JT = numpy.linalg.solve(V, J.T)
        ri_diag = numpy.einsum('rj,jr->r', J, Vinv_JT)
        # Exact (rs|rs)_L,M for each row of J -- reproduce the same row
        # ordering used by orbital_aux_projection.
        exact = []
        fourpi_2Lp1 = 4.0 * pi / (2 * L + 1)
        for la, n_a, aa in primitives:
            Na = gto_norm(n_a, aa)
            for lb, n_b, ab in primitives:
                if L not in coupling_lvals(la, lb):
                    continue
                Nb = gto_norm(n_b, ab)
                n_ab = n_a + n_b
                a_ab = aa + ab
                R_diag = radial_integral(L, n_ab, n_ab, a_ab, a_ab)
                G = gaunt_table(la, lb, L)
                for ima in range(2*la + 1):
                    for imb in range(2*lb + 1):
                        for iM in range(2*L + 1):
                            g = G[ima, imb, iM]
                            if g == 0.0:
                                continue
                            exact.append(fourpi_2Lp1 * (g*g) * (Na*Nb)**2 * R_diag)
        exact = numpy.asarray(exact)
        err += float(numpy.sum(exact - ri_diag))
    return err


@pytest.mark.slow
def test_generated_aux_diagonal_ri_error_fe_def2_qzvpp():
    """Calibrated benchmark against the 2021 paper Fe entry: the
    primitive (uncontracted, unpruned) Cholesky selection with
    ``n_random = 100`` and ``tau = 1e-7`` must produce a total diagonal
    RI error below ``1.2e-3 Eh`` for Fe def2-QZVPP.  This is the
    headline figure that motivates the algorithm; a regression here
    would indicate selection-quality drift.
    """
    tau = 1.0e-7
    b = get_basis('def2-QZVPP', elements=[26])
    aux = generate_auxiliary_basis(b, elements=[26], threshold=tau,
                                   contract=False, prune_lmax=False,
                                   n_random=100, seed=0)
    err = _diag_ri_error_primitive_aux(b['elements']['26'],
                                       aux['elements']['26'])
    assert err >= -1e-12, f"diagonal RI error must be non-negative, got {err}"
    assert err < 1.2e-3, \
        f"Fe def2-QZVPP diagonal RI error {err} >= 1.2e-3 at tau={tau}"


def test_generated_aux_diagonal_ri_error_bounded():
    """The pivoted-Cholesky selection guarantees that, for the primitive
    auxiliary basis generated with drop tolerance ``tau``, the diagonal
    RI error of every orbital-product channel is bounded -- so the sum
    over all orbital primitive products is bounded by ``tau`` times the
    number of orbital products.
    """
    tau = 1.0e-5
    b = get_basis('cc-pVDZ', elements=[6])
    aux = generate_auxiliary_basis(b, elements=[6], threshold=tau,
                                   contract=False, prune_lmax=False,
                                   n_random=0)
    err = _diag_ri_error_primitive_aux(b['elements']['6'], aux['elements']['6'])
    assert err >= -1e-12, f"diagonal RI error must be non-negative, got {err}"
    # Loose-but-meaningful bound: error per orbital-primitive-product
    # times number of products, with some headroom.
    from basis_set_exchange.auxgen.products import decontract_primitives
    n_prims_m = sum(2*l + 1 for l, _n, _a in decontract_primitives(b['elements']['6']))
    bound = tau * n_prims_m**2
    assert err < bound, f"diagonal RI error {err} >= bound {bound}"


# ---------------------------------------------------------------------------
# CLI handler smoke test
# ---------------------------------------------------------------------------

def test_cli_autogen_aux_smoke(tmp_path):
    """End-to-end through the CLI: get-basis -> autogen-aux -> readback.
    Exercises argument parsing, file I/O, and the handler glue.  The
    algorithmic content is covered by the other tests; this catches CLI
    regressions in flag wiring."""
    import argparse
    from basis_set_exchange.cli.bse_handlers import _bse_cli_autogen_aux
    from basis_set_exchange import readers

    # Write a small orbital basis to a Gaussian94 file via BSE.
    b = get_basis('cc-pVDZ', elements=[1])
    b.setdefault('function_types', ['gto_spherical'])
    in_path = tmp_path / 'in.gbs'
    in_path.write_text(write_formatted_basis_str(b, 'gaussian94'))
    out_path = tmp_path / 'out.gbs'

    args = argparse.Namespace(
        input_file=str(in_path),
        output_file=str(out_path),
        in_fmt=None,
        out_fmt=None,
        threshold=1.0e-5,
        scheme='reduced',
        n_random=0,
        seed=0,
        mapping='moment',
        collapse_contractions=None,
        size=None,
        contract=True,
        contract_threshold=1.0e-5,
        prune_lmax=True,
        linc=1,
    )
    msg = _bse_cli_autogen_aux(args)
    assert 'auxgen' in msg.lower()
    assert out_path.exists() and out_path.stat().st_size > 0
    out = readers.read_formatted_basis_file(str(out_path), 'gaussian94')
    assert '1' in out['elements']
    assert len(out['elements']['1']['electron_shells']) > 0


# ---------------------------------------------------------------------------
# api.get_basis(..., get_aux=...) integration
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('mode,size', [
    ('cholesky-small', 'small'),
    ('cholesky-large', 'large'),
    ('cholesky-verylarge', 'verylarge'),
])
def test_get_basis_cholesky_aux(mode, size):
    """``get_aux='cholesky-*'`` dispatches to the auxgen Cholesky driver with
    the matching size preset, attaches the right metadata, and yields a basis
    that round-trips through a writer."""
    aux = get_basis('cc-pVDZ', elements=[1, 6], get_aux=mode)
    assert aux['name'].endswith('_aux_cholesky_' + size)
    assert aux['role'] == 'rifit'
    assert aux['function_types'] == ['gto_spherical']
    assert set(aux['elements'].keys()) == {'1', '6'}
    for el in aux['elements'].values():
        shells = el['electron_shells']
        assert len(shells) > 0
        # All shells must be valid GTOs
        for sh in shells:
            assert len(sh['exponents']) == len(sh['coefficients'][0])
    # Sizes should be ordered small <= large <= verylarge in shell count
    text = write_formatted_basis_str(aux, 'nwchem')
    assert 'BASIS' in text


def test_get_basis_cholesky_sizes_ordered():
    """small <= large <= verylarge in total primitive count (paper Table 1)."""
    counts = []
    for mode in ('cholesky-small', 'cholesky-large', 'cholesky-verylarge'):
        aux = get_basis('cc-pVDZ', elements=[6], get_aux=mode)
        n = sum(len(sh['exponents']) for sh in aux['elements']['6']['electron_shells'])
        counts.append(n)
    assert counts[0] <= counts[1] <= counts[2]


@pytest.mark.parametrize('alias,mode', [
    (0, None),
    (1, 'autoaux'),
    (2, 'autoabs'),
    (3, 'cholesky-small'),
    (4, 'cholesky-large'),
    (5, 'cholesky-verylarge'),
])
def test_get_aux_legacy_int_alias(alias, mode):
    """Legacy ``get_aux=<int>`` must produce the same output as the canonical
    string form."""
    from basis_set_exchange.api import _normalize_get_aux
    assert _normalize_get_aux(alias) == mode


@pytest.mark.parametrize('value', [None, 'NONE', 'none', '', 0])
def test_get_aux_none_aliases(value):
    """None/'', 'none' (any case), and the integer 0 all mean "orbital basis"."""
    from basis_set_exchange.api import _normalize_get_aux
    assert _normalize_get_aux(value) is None


@pytest.mark.parametrize('value', [True, False, 6, -1, 'cholesky-medium', 'autoaux2', 1.5])
def test_get_aux_rejects_garbage(value):
    """Bad input is rejected with ValueError or TypeError, not silently coerced."""
    from basis_set_exchange.api import _normalize_get_aux
    with pytest.raises((TypeError, ValueError)):
        _normalize_get_aux(value)


def test_get_aux_case_insensitive():
    """String input is folded to lower-case."""
    aux_lower = get_basis('cc-pVDZ', elements=[1], get_aux='autoaux')
    aux_upper = get_basis('cc-pVDZ', elements=[1], get_aux='AutoAux')
    assert aux_lower['name'] == aux_upper['name']


# ---------------------------------------------------------------------------
# STO driver (basis_set_exchange.auxgen.sto)
# ---------------------------------------------------------------------------

def test_sto_norm_overlap_unity():
    """sto_norm(n, zeta) is the constant that makes the un-normalised
    radial r^(n-1) e^(-zeta r) have unit overlap when paired with a
    normalised Y_LM."""
    from basis_set_exchange.auxgen.sto import sto_norm
    from math import gamma
    for (n, z) in [(1, 1.0), (1, 0.76), (2, 1.5), (3, 2.5), (4, 0.3)]:
        N = sto_norm(n, z)
        # int_0^inf (N r^(n-1))^2 e^(-2 z r) r^2 dr = 1
        radial_sq = N * N * gamma(2 * n + 1) / (2.0 * z) ** (2 * n + 1)
        assert radial_sq == pytest.approx(1.0, rel=1e-13)


def test_sto_radial_coulomb_h_1s_slater():
    """Hydrogen 1s self-repulsion (1s,1s|1s,1s) = 5 zeta / 8 (Slater)."""
    from basis_set_exchange.auxgen.sto import sto_norm, sto_radial_coulomb
    for zeta in (1.0, 1.5, 2.7):
        N = sto_norm(1, zeta)
        # m=N_a+1=2, n=N_b+1=2, v=0 (monopole), x=y=2 zeta.
        # Angular factor 4pi * G(0,0,0,0,0,0)^2 = 1.
        val = N**4 * sto_radial_coulomb(2, 2, 0, 2 * zeta, 2 * zeta)
        assert val == pytest.approx(5.0 * zeta / 8.0, rel=1e-13)


def test_sto_aux_metric_unit_diagonal():
    """Coulomb-normalised aux metric must have (P|P) = 1."""
    from basis_set_exchange.auxgen.sto import sto_aux_metric
    for L, items in [
        (0, [(1, 1.0), (1, 2.5), (1, 0.4)]),
        (1, [(2, 1.0), (2, 0.7)]),
        (2, [(3, 1.5)]),
    ]:
        V = sto_aux_metric(L, items)
        assert numpy.allclose(numpy.diag(V), 1.0, atol=1e-13)
        # Symmetric, positive definite.
        assert numpy.allclose(V, V.T, atol=1e-13)
        eig = numpy.linalg.eigvalsh(V)
        assert eig.min() > 0


def test_sto_one_electron_matrices_h_1s():
    """For an STO basis at the H atom, T + V_nuc + Z/r = -1/2 Hartree
    for the 1s with zeta=1; for general zeta the energy is
    zeta^2/2 - zeta and is minimised at zeta=1 with E=-1/2.
    """
    from basis_set_exchange.auxgen.sto import (
        sto_overlap_matrix, sto_kinetic_matrix, sto_nuclear_attraction_matrix,
    )
    for zeta in (0.7, 1.0, 1.6):
        S = sto_overlap_matrix([(1, zeta)])
        T = sto_kinetic_matrix(0, [(1, zeta)])
        V = sto_nuclear_attraction_matrix([(1, zeta)])    # +<chi|1/r|chi>
        # Normalise the 1x1 expectation values
        norm2 = S[0, 0]
        E = (T[0, 0] - V[0, 0]) / norm2
        assert E == pytest.approx(0.5 * zeta * zeta - zeta, rel=1e-12)


def test_sto_candidate_pool_preserves_n():
    """The STO candidate pool must keep the natural radial power
    ``n_aux = n_a + n_b - 1`` rather than collapse onto ``n_aux = L+1``;
    standard STO aux sets need the high-n character that a collapse
    would discard.
    """
    from basis_set_exchange.auxgen.sto import sto_candidate_pool_from_primitives
    # 1s (n=1) and 2p (n=2) primitives.
    prims = [(0, 1, 1.0), (1, 2, 1.5)]
    pool = sto_candidate_pool_from_primitives(prims)
    # 1s*1s -> L=0, n=1; 1s*2p -> L=1, n=2; 2p*2p -> L=0, n=3 and L=2, n=3
    n_at_L = {L: sorted({n for (n, _z) in items}) for L, items in pool.items()}
    assert n_at_L[0] == [1, 3]      # 1s*1s gives n=1; 2p*2p gives n=3
    assert n_at_L[1] == [2]         # 1s*2p gives n=2
    assert n_at_L[2] == [3]         # 2p*2p gives n=3


def test_sto_generate_basic_and_reduced_agree_on_simple():
    """For an STO basis where the candidate pool exactly spans the
    orbital products (a few S primitives, distinct exponents), both
    schemes select the same number of aux functions and the diagonal
    RI error is essentially zero."""
    from basis_set_exchange.auxgen.sto import (
        generate_sto_auxiliary_basis, sto_diagonal_ri_error,
    )
    sto = {0: [(1, 0.5), (1, 1.0), (1, 2.0)]}
    aux_basic = generate_sto_auxiliary_basis(sto, threshold=1e-9,
                                              scheme='basic', n_random=0)
    aux_reduced = generate_sto_auxiliary_basis(sto, threshold=1e-9,
                                                scheme='reduced', n_random=0)
    n_basic = sum(len(v) for v in aux_basic.values())
    n_reduced = sum(len(v) for v in aux_reduced.values())
    assert n_basic == n_reduced
    err_basic = sto_diagonal_ri_error(sto, aux_basic)
    err_reduced = sto_diagonal_ri_error(sto, aux_reduced)
    assert err_basic == pytest.approx(0.0, abs=1e-12)
    assert err_reduced == pytest.approx(0.0, abs=1e-12)


def test_sto_ri_error_nonneg_and_decreases_with_threshold():
    """Tighter Cholesky threshold => smaller (or equal) diagonal RI error."""
    from basis_set_exchange.auxgen.sto import (
        generate_sto_auxiliary_basis, sto_diagonal_ri_error,
    )
    sto = {0: [(1, 2.0), (1, 1.0), (2, 0.5)],
           1: [(2, 1.5), (2, 0.7)]}
    errors = []
    for tau in (1e-3, 1e-5, 1e-7, 1e-9):
        aux = generate_sto_auxiliary_basis(sto, threshold=tau,
                                            scheme='reduced', n_random=0)
        err = sto_diagonal_ri_error(sto, aux)
        # RI is variational from below per orbital pair: err >= 0 (FP noise).
        assert err >= -1e-12
        errors.append(err)
    # Monotone non-increasing (modulo small FP noise).
    for prev, cur in zip(errors, errors[1:]):
        assert cur <= prev + 1e-12


def test_sto_compact_collapses_to_min_n():
    """``compact=True`` must produce an aux basis with ``n == L + 1`` at
    every L, while leaving the diagonal RI error finite (it may be
    larger than the default mode -- compact discards radial richness)."""
    from basis_set_exchange.auxgen.sto import (
        generate_sto_auxiliary_basis, sto_diagonal_ri_error,
    )
    sto = {0: [(1, 1.5), (2, 0.7)], 1: [(2, 1.2), (3, 0.5)]}
    aux = generate_sto_auxiliary_basis(sto, threshold=1e-7, scheme='basic',
                                        n_random=0, compact=True)
    for L, items in aux.items():
        for (n, _z) in items:
            assert n == L + 1
    # Should still produce a usable, non-negative RI error.
    err = sto_diagonal_ri_error(sto, aux)
    assert err >= -1e-12


def test_sto_compact_vs_default_pool_diversity():
    """The default (n-preserving) mode must produce >=1 candidate
    n-value larger than L+1 for at least one L when the orbital basis
    has primitives with n > l+1; the compact mode never does."""
    from basis_set_exchange.auxgen.sto import (
        sto_candidate_pool_from_primitives, _compact_pool,
    )
    # 2p (n=2) and 3d (n=3) -> products at L=1,3 (p*d) and L=0,2,4 (d*d)
    # with n_aux = 2+3-1 = 4 and 3+3-1 = 5 (above L+1).
    prims = [(1, 2, 1.5), (2, 3, 1.0)]
    natural = sto_candidate_pool_from_primitives(prims)
    compact = _compact_pool(natural)
    # natural has at least one n > L + 1
    has_high_n = any(n > L + 1 for L, items in natural.items() for (n, _z) in items)
    assert has_high_n
    # compact never does
    for L, items in compact.items():
        for (n, _z) in items:
            assert n == L + 1


def test_sto_prune_lmax_drops_high_l():
    """prune_lmax=True must cap the output angular momentum at l_keep
    (Lehtola 2023 eq 9) given lmax_occ."""
    from basis_set_exchange.auxgen.sto import generate_sto_auxiliary_basis
    sto = {0: [(1, 1.0)], 1: [(2, 1.5)], 2: [(3, 1.2)], 3: [(4, 0.9)]}
    # H (lmax_occ=0): l_keep = max(0, 0 + 3 + 1) = 4 -> no shells dropped here.
    aux = generate_sto_auxiliary_basis(sto, threshold=1e-7,
                                        prune_lmax=True, lmax_occ=0, linc=1)
    # With l_keep=4 nothing is dropped; this just exercises the code path.
    assert all(L <= 4 for L in aux.keys())
    # With linc=0 and lmax_occ=0, l_keep = max(0, 0+3+0) = 3 -> shells with
    # L>3 would be dropped (none here, but invariant holds).
    aux2 = generate_sto_auxiliary_basis(sto, threshold=1e-7,
                                         prune_lmax=True, lmax_occ=0, linc=0)
    assert all(L <= 3 for L in aux2.keys())


def test_sto_adf_roundtrip(tmp_path):
    """End-to-end: parse an ADF basis text, regenerate the FIT block,
    write it back, re-parse, and check that BASIS is preserved and FIT
    is replaced with the new candidate set."""
    from basis_set_exchange.auxgen.sto import (
        read_adf_basis, write_adf_basis, generate_sto_auxiliary_basis,
    )
    text = (
        "Hydrogen (test)\n"
        "\n"
        "BASIS\n"
        "1S   0.76\n"
        "1S   1.28\n"
        "END\n"
        "\n"
        "CORE    0  0  0  0\n"
        "END\n"
        "\n"
        "DESCRIPTION\n"
        "test STO basis for the auxgen.sto roundtrip\n"
        "END\n"
        "\n"
        "FIT\n"
        " 1S   3.16\n"
        " 1S   2.09\n"
        " 1S   1.38\n"
        "END\n"
        "\n"
        "FITCOEFFICIENTS\n"
        "/\n"
        "END\n"
    )
    in_path = tmp_path / 'h.adf'
    in_path.write_text(text)
    parsed = read_adf_basis(str(in_path))
    assert parsed['orbital'] == {0: [(1, 0.76), (1, 1.28)]}
    assert parsed['fit'] == {0: [(1, 3.16), (1, 2.09), (1, 1.38)]}

    new_fit = generate_sto_auxiliary_basis(parsed['orbital'], threshold=1e-9,
                                            scheme='basic', n_random=0)
    out_path = tmp_path / 'h_out.adf'
    write_adf_basis(str(out_path), parsed, new_fit)
    re_parsed = read_adf_basis(str(out_path))
    assert re_parsed['orbital'] == parsed['orbital']
    # New FIT must contain the (1, 1.52), (1, 2.04), (1, 2.56) standard-
    # primitive exponents that exactly span the 1s*1s products.
    re_zetas = sorted(z for (_n, z) in re_parsed['fit'][0])
    assert re_zetas == pytest.approx([1.52, 2.04, 2.56], rel=1e-10)


def test_sto_main_driver_runs_on_adf_file(tmp_path):
    """Smoke test for the ``python -m basis_set_exchange.auxgen.sto``
    driver: regenerate the FIT block on an ADF file and write the result
    out without crashing."""
    from basis_set_exchange.auxgen.sto import main
    in_text = (
        "Hydrogen (test)\n\n"
        "BASIS\n1S 0.76\n1S 1.28\nEND\n\n"
        "CORE    0  0  0  0\nEND\n\n"
        "DESCRIPTION\nEND\n\n"
        "FIT\n 1S 3.16\n 1S 2.09\n 1S 1.38\nEND\n\n"
        "FITCOEFFICIENTS\n/\nEND\n"
    )
    in_path = tmp_path / 'h.adf'
    in_path.write_text(in_text)
    out_path = tmp_path / 'h_new.adf'
    rc = main([str(in_path), str(out_path), '--threshold', '1e-9',
               '--scheme', 'basic', '--no-benchmark'])
    assert rc == 0
    assert out_path.exists() and out_path.stat().st_size > 0

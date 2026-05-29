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

import basis_set_exchange as bse
from basis_set_exchange.auxgen.gaunt import real_gaunt, coupling_lvals
from basis_set_exchange.auxgen.radial import (
    radial_integral, gto_norm, alpha_eff,
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
    pyscf = pytest.importorskip('pyscf')
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
    b = bse.get_basis('cc-pVDZ', elements=[1])
    aux = generate_auxiliary_basis(b, threshold=1e-7, scheme=scheme,
                                   contract=False, prune_lmax=False)
    shells = aux['elements']['1']['electron_shells']
    assert len(shells) >= 5
    # All shells are spherical Gaussians with one primitive each
    for s in shells:
        assert s['function_type'] == 'gto_spherical'
        assert len(s['exponents']) == 1


def test_end_to_end_contracted():
    b = bse.get_basis('cc-pVDZ', elements=[6])
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
    b = bse.get_basis('cc-pVDZ', elements=[6])
    det = generate_auxiliary_basis(b, threshold=1e-7, scheme='basic',
                                    n_random=0)
    rnd = generate_auxiliary_basis(b, threshold=1e-7, scheme='basic',
                                    n_random=32, seed=0)
    nd = len(det['elements']['6']['electron_shells'])
    nr = len(rnd['elements']['6']['electron_shells'])
    assert nr <= nd


def test_random_seed_reproducibility():
    b = bse.get_basis('cc-pVDZ', elements=[6])
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
    b = bse.get_basis('cc-pVDZ', elements=[6])
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
    b = bse.get_basis('cc-pVDZ', elements=[6])
    a_loose = generate_auxiliary_basis(b, threshold=1.0e-3,
                                        scheme='basic', n_random=0)
    a_tight = generate_auxiliary_basis(b, threshold=1.0e-8,
                                        scheme='basic', n_random=0)
    nl = len(a_loose['elements']['6']['electron_shells'])
    nt = len(a_tight['elements']['6']['electron_shells'])
    assert nt >= nl


def test_end_to_end_lmax_pruning():
    b = bse.get_basis('cc-pVDZ', elements=[6])
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

def test_contracted_functions_coulomb_normalized():
    """Every contracted auxiliary function must be normalized to
    (A|A) = 1 in the Coulomb metric (not the overlap metric), with the
    output coefficients in the overlap-normalized primitive convention."""
    from basis_set_exchange.auxgen.twoel import primitive_aux_metric

    b = bse.get_basis('cc-pVTZ', elements=[8])
    aux = generate_auxiliary_basis(b, elements=[8], threshold=1e-7,
                                   contract=True, contract_threshold=1e-5,
                                   prune_lmax=False)
    for s in aux['elements']['8']['electron_shells']:
        L = s['angular_momentum'][0]
        exps = [float(e) for e in s['exponents']]
        V = primitive_aux_metric(L, exps)
        for coeff in s['coefficients']:
            c = numpy.array([float(x) for x in coeff])
            aa = c @ V @ c
            assert abs(aa - 1.0) < 1e-8, f"L={L}: (A|A)={aa}, expected 1"


@pytest.mark.parametrize('size,eps,linc', [
    ('verylarge', 1e-6, 1),
    ('large', 1e-5, 1),
    ('small', 1e-4, 0),
])
def test_size_presets_match_paper(size, eps, linc):
    """The size presets must reproduce the (epsilon, l_inc) pairs of the
    2023 paper and force contraction + lmax pruning on."""
    b = bse.get_basis('cc-pVTZ', elements=[8])
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
    b = bse.get_basis('cc-pVTZ', elements=[8])
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
    pyscf = pytest.importorskip('pyscf')
    from pyscf import gto, scf
    from basis_set_exchange import writers

    elem = 'Ne'
    b = bse.get_basis('cc-pVDZ', elements=[elem])
    aux_prim = generate_auxiliary_basis(b, threshold=1e-8, contract=False,
                                        prune_lmax=False)
    aux_contr = generate_auxiliary_basis(b, threshold=1e-8, contract=True,
                                         contract_threshold=1e-5, prune_lmax=False)

    def to_pyscf(aux):
        aux = dict(aux)
        aux.setdefault('function_types', ['gto_spherical'])
        aux.setdefault('names', ['auxgen'])
        return gto.basis.parse(writers.write_formatted_basis_str(aux, 'nwchem'))

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
    b = bse.get_basis('cc-pVDZ', elements=[8])
    a_default = generate_auxiliary_basis(b, elements=[8])
    a_moment = generate_auxiliary_basis(b, elements=[8], mapping='moment')
    assert a_default == a_moment
    # 'selfrepulsion' is accepted and produces a valid basis
    a_sr = generate_auxiliary_basis(b, elements=[8], mapping='selfrepulsion')
    assert len(a_sr['elements']['8']['electron_shells']) > 0


# ---------------------------------------------------------------------------
# Single-primitive replacement of contracted orbital functions (selection)
# ---------------------------------------------------------------------------

def test_match_single_primitive_within_range_and_identity():
    from basis_set_exchange.auxgen.products import _match_single_primitive
    # A single-term "contraction" recovers its own exponent.
    assert abs(_match_single_primitive(0, [2.5], [1.0]) - 2.5) < 1e-6
    # A two-term contraction maps to an exponent strictly between them.
    beta = _match_single_primitive(0, [1.0, 16.0], [0.6, 0.6])
    assert 1.0 < beta < 16.0


def test_collapse_contractions_one_primitive_per_contracted_function():
    from basis_set_exchange.auxgen.products import (
        decontract_primitives, decontract_primitives_single,
    )
    b = bse.get_basis('cc-pVDZ', elements=[6])  # (9s,4p,1d) -> [3s,2p,1d]
    eb = b['elements']['6']
    single = decontract_primitives_single(eb)
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
    b = bse.get_basis('cc-pVDZ', elements=[6])
    a_default = generate_auxiliary_basis(b, elements=[6])
    a_off = generate_auxiliary_basis(b, elements=[6], collapse_contractions=False)
    assert a_default == a_off
    a_on = generate_auxiliary_basis(b, elements=[6], collapse_contractions=True)
    assert len(a_on['elements']['6']['electron_shells']) > 0

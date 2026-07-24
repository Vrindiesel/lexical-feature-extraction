"""
Created by davan (with Claude assistance)
7/23/26

T3 — stats cross-check: the hand-rolled test family against scipy on
seeded (deterministic) data, plus fixed golden values for the chi-square
survival function. The hand-rolled versions apply no tie correction, so
the random cross-checks use continuous floats (ties have probability ~0).
"""

import random

import pytest

from lexfeat import stats

scipy_stats = pytest.importorskip("scipy.stats")

RNG_SEED = 20260723


def _random_groups(rng, sizes):
    return [[rng.random() for _ in range(n)] for n in sizes]


def test_kruskal_wallis_vs_scipy():
    rng = random.Random(RNG_SEED)
    groups = _random_groups(rng, [40, 35, 50, 45])
    h, p, df = stats.kruskal_wallis(groups)
    h_sp, p_sp = scipy_stats.kruskal(*groups)
    assert df == 3
    assert h == pytest.approx(h_sp, rel=1e-10)
    assert p == pytest.approx(p_sp, rel=1e-8)


def test_mann_whitney_vs_scipy():
    rng = random.Random(RNG_SEED + 1)
    x = [rng.random() for _ in range(60)]
    y = [rng.gauss(0.6, 0.2) for _ in range(45)]
    u, p = stats.mann_whitney_u(x, y)
    res = scipy_stats.mannwhitneyu(x, y, alternative="two-sided",
                                   use_continuity=False, method="asymptotic")
    u_sp = min(res.statistic, len(x) * len(y) - res.statistic)
    assert u == pytest.approx(u_sp, rel=1e-12)
    assert p == pytest.approx(res.pvalue, rel=1e-8)


def test_chi2_2xk_vs_scipy():
    rng = random.Random(RNG_SEED + 2)
    groups = [[1 if rng.random() < q else 0 for _ in range(n)]
              for q, n in [(0.6, 120), (0.45, 90), (0.4, 150), (0.35, 200)]]
    chi2, p, df = stats.chi2_2xk(groups)
    table = [[sum(g) for g in groups], [len(g) - sum(g) for g in groups]]
    chi2_sp, p_sp, df_sp, _ = scipy_stats.chi2_contingency(table, correction=False)
    assert df == df_sp
    assert chi2 == pytest.approx(chi2_sp, rel=1e-10)
    assert p == pytest.approx(p_sp, rel=1e-8)


def test_chi2_2x2_vs_scipy():
    g1 = [1] * 55 + [0] * 45
    g2 = [1] * 30 + [0] * 70
    chi2, p, df = stats.chi2_2x2(g1, g2)
    table = [[55, 30], [45, 70]]
    chi2_sp, p_sp, _, _ = scipy_stats.chi2_contingency(table, correction=False)
    assert df == 1
    assert chi2 == pytest.approx(chi2_sp, rel=1e-10)
    assert p == pytest.approx(p_sp, rel=1e-8)


def test_chi2_sf_golden_values():
    # scipy.stats.chi2.sf reference values, fixed at port time
    golden = [
        ((1.0, 1), 0.31731050786291115),
        ((5.2, 3), 0.15772445039666255),
        ((144.7, 1), 2.497749352813608e-33),
        ((1026.2, 3), 3.728035091777096e-222),
        ((0.5, 10), 0.999993388289439),
        ((30.0, 2), 3.0590232050182594e-07),
    ]
    for (x, df), want in golden:
        assert stats.chi2_sf(x, df) == pytest.approx(want, rel=1e-10)
    assert stats.chi2_sf(0.0, 5) == 1.0
    assert stats.chi2_sf(-1.0, 5) == 1.0


def test_effect_and_correction_helpers():
    assert stats.cramers_v(4.0, 100) == pytest.approx(0.2)
    assert stats.cramers_v(4.0, 0) == 0
    assert stats.rank_biserial_r(0.0, 10, 10) == 1.0
    assert stats.rank_biserial_r(50.0, 10, 10) == 0.0
    assert stats.bonferroni(0.01, 25) == 0.25
    assert stats.bonferroni(0.2, 25) == 1.0
    assert stats.sig_stars(0.0005) == "***"
    assert stats.sig_stars(0.005) == "**"
    assert stats.sig_stars(0.03) == "*"
    assert stats.sig_stars(0.2) == "n.s."

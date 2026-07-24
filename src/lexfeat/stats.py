"""
Created by davan (with Claude assistance)
7/23/26

Statistical tests as implemented for the IVA 2026 paper (hand-rolled,
stdlib-only).

These are the paper's implementations, ported behaviorally verbatim: the
published test statistics and p-values were produced by exactly this
arithmetic. Kruskal-Wallis and Mann-Whitney U use average ranks with no tie
correction and a normal approximation without continuity correction; the
chi-square survival function is computed from the regularized incomplete
gamma series. CI cross-validates the family against scipy on tie-free data.
"""

import math


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _rank_data(values):
    """Average ranks (1-based) with ties sharing their mean rank."""
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    n = len(indexed)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def chi2_sf(x: float, df: float) -> float:
    """Chi-square survival function via the regularized incomplete gamma."""
    if x <= 0 or df <= 0:
        return 1.0
    a = df / 2.0
    z = x / 2.0
    if z > a + 1:
        return _upper_reg_gamma(a, z)
    else:
        return 1.0 - _lower_reg_gamma(a, z)


def _lower_reg_gamma(a, x):
    if x <= 0:
        return 0.0
    gln = math.lgamma(a)
    ap = a
    sum_val = 1.0 / a
    delta = sum_val
    for _ in range(1, 500):
        ap += 1
        delta *= x / ap
        sum_val += delta
        if abs(delta) < abs(sum_val) * 1e-12:
            break
    log_val = -x + a * math.log(x) - gln
    if log_val < -700:
        return 0.0
    return sum_val * math.exp(log_val)


def _upper_reg_gamma(a, x):
    if x <= 0:
        return 1.0
    gln = math.lgamma(a)
    FPMIN = 1e-300
    b = x + 1.0 - a
    c = 1.0 / FPMIN
    d = 1.0 / b if b != 0 else 1.0 / FPMIN
    h = d
    for i in range(1, 300):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < FPMIN:
            d = FPMIN
        c = b + an / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    log_val = -x + a * math.log(x) - gln
    if log_val < -700:
        return 0.0
    return h * math.exp(log_val)


def kruskal_wallis(groups: list) -> tuple:
    """Kruskal-Wallis H over a list of value lists; returns (H, p, df)."""
    all_vals = []
    group_ids = []
    for gid, vals in enumerate(groups):
        all_vals.extend(vals)
        group_ids.extend([gid] * len(vals))
    N = len(all_vals)
    if N < 4:
        return 0.0, 1.0, 0
    ranks = _rank_data(all_vals)
    k = len(groups)
    group_rank_sums = [0.0] * k
    group_ns = [0] * k
    for rank, gid in zip(ranks, group_ids):
        group_rank_sums[gid] += rank
        group_ns[gid] += 1
    H = (12.0 / (N * (N + 1))) * sum(
        (group_rank_sums[i] ** 2) / group_ns[i] for i in range(k) if group_ns[i] > 0
    ) - 3 * (N + 1)
    df = k - 1
    p_val = chi2_sf(H, df)
    return H, p_val, df


def mann_whitney_u(x: list, y: list) -> tuple:
    """Mann-Whitney U (two-sided, normal approximation); returns (U, p)."""
    nx, ny = len(x), len(y)
    if nx == 0 or ny == 0:
        return 0.0, 1.0
    all_vals = list(x) + list(y)
    ranks = _rank_data(all_vals)
    R1 = sum(ranks[:nx])
    U1 = R1 - nx * (nx + 1) / 2
    U2 = nx * ny - U1
    U = min(U1, U2)
    mu = nx * ny / 2.0
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12.0)
    if sigma == 0:
        return U, 1.0
    z = (U - mu) / sigma
    p_val = 2 * (1 - _norm_cdf(abs(z)))
    return U, p_val


def chi2_2xk(groups_binary: list) -> tuple:
    """Chi-square on a 2xk table of binary outcomes; returns (chi2, p, df)."""
    k = len(groups_binary)
    observed_yes = [sum(g) for g in groups_binary]
    observed_no = [len(g) - sum(g) for g in groups_binary]
    N = sum(len(g) for g in groups_binary)
    total_yes = sum(observed_yes)
    total_no = sum(observed_no)
    if total_yes == 0 or total_no == 0 or N == 0:
        return 0.0, 1.0, 0
    chi2 = 0.0
    for i in range(k):
        ni = len(groups_binary[i])
        if ni == 0:
            continue
        exp_yes = ni * total_yes / N
        exp_no = ni * total_no / N
        if exp_yes > 0:
            chi2 += (observed_yes[i] - exp_yes) ** 2 / exp_yes
        if exp_no > 0:
            chi2 += (observed_no[i] - exp_no) ** 2 / exp_no
    df = k - 1
    p_val = chi2_sf(chi2, df)
    return chi2, p_val, df


def chi2_2x2(g1: list, g2: list) -> tuple:
    """Chi-square on a 2x2 table (no Yates correction); returns (chi2, p, df)."""
    return chi2_2xk([g1, g2])


def cramers_v(chi2: float, n: int) -> float:
    """Cramér's V for a 2x2 chi-square."""
    return math.sqrt(chi2 / n) if n > 0 else 0


def rank_biserial_r(u: float, nx: int, ny: int) -> float:
    """Rank-biserial correlation from a Mann-Whitney U (U = min(U1, U2))."""
    return 1 - (2 * u) / (nx * ny) if (nx * ny) > 0 else 0


def bonferroni(p: float, n_tests: int) -> float:
    """Bonferroni-corrected p-value, capped at 1.0."""
    return min(p * n_tests, 1.0)


def sig_stars(p_val: float) -> str:
    """Significance stars: *** < .001, ** < .01, * < .05, else n.s."""
    if p_val < 0.001:
        return "***"
    elif p_val < 0.01:
        return "**"
    elif p_val < 0.05:
        return "*"
    else:
        return "n.s."

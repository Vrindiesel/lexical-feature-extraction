"""
Created by davan (with Claude assistance)
7/23/26

Rates-by-label analysis driver: omnibus and pairwise tests over a profile.

rates_by_label reproduces the computation of the original run_analysis
(the function that produced the IVA 2026 Tables 4 and 6): per-feature rates
or means by label, an omnibus test across all labels, a configurable
pairwise contrast with effect size, and Bonferroni correction across the
profile's feature count. Feature order, arithmetic, and test choices are
identical to the original.
"""

from collections import defaultdict

from lexfeat import stats
from lexfeat.features import clean_text
from lexfeat.profiles import FEATURE_FORMATS

# Features whose value is None when undefined; None values are excluded
# from means and tests, exactly as in the original analysis.
CONDITIONAL_FEATURES = ("hedge_ratio", "self_ratio")


def rates_by_label(records, profile, label_key: str = "label", text_key: str = "text",
                   labels: tuple = ("A", "B", "C", "D"), pairwise: tuple = ("A", "B"),
                   correction: str = "bonferroni") -> dict:
    """Run the per-feature rates and significance analysis over records.

    records: iterable of dicts carrying a text field and a label field;
    records with a falsy label are skipped. Text is SSML-stripped with
    clean_text before extraction, matching the original pipeline. Returns
    {"labels", "pairwise", "n_features", "features": [per-feature dicts]}
    — the object the report writers consume.
    """
    if correction != "bonferroni":
        raise ValueError("Invalid correction (only 'bonferroni' is supported)")

    label_features = defaultdict(list)
    for r in records:
        label = r.get(label_key)
        if not label:
            continue
        label_features[label].append(profile.extract(clean_text(r.get(text_key, ""))))

    results = []
    n_features = len(profile.features)

    for feature in profile.features:
        feat_key = feature.id
        is_binary = feature.kind == "binary"
        fmt = FEATURE_FORMATS.get(feat_key, "{:.1%}" if is_binary else "{:.3f}")

        vals_by_label = {lab: [f[feat_key] for f in label_features[lab]] for lab in labels}

        is_conditional = feat_key in CONDITIONAL_FEATURES
        if is_conditional:
            vals_by_label = {
                lab: [v for v in vs if v is not None]
                for lab, vs in vals_by_label.items()
            }

        label_stats = {}
        for lab in labels:
            vs = vals_by_label[lab]
            label_stats[lab] = sum(vs) / len(vs) if vs else 0.0

        groups_for_test = [vals_by_label[lab] for lab in labels]
        if is_binary:
            omni_stat, omni_p, _ = stats.chi2_2xk(groups_for_test)
            omni_test = "chi2"
        else:
            omni_stat, omni_p, _ = stats.kruskal_wallis(groups_for_test)
            omni_test = "K-W"

        a_vals = vals_by_label[pairwise[0]]
        b_vals = vals_by_label[pairwise[1]]
        na, nb = len(a_vals), len(b_vals)
        if is_binary:
            ab_stat, ab_p, _ = stats.chi2_2x2(a_vals, b_vals)
            ab_test = "chi2"
            effect_size = stats.cramers_v(ab_stat, na + nb)
            effect_name = "Cramer_V"
        else:
            ab_stat, ab_p = stats.mann_whitney_u(a_vals, b_vals)
            ab_test = "M-W"
            effect_size = stats.rank_biserial_r(ab_stat, na, nb)
            effect_name = "rank_biserial_r"

        ab_diff = label_stats[pairwise[0]] - label_stats[pairwise[1]]

        results.append({
            "key": feat_key,
            "display": feature.name,
            "is_binary": is_binary,
            "fmt": fmt,
            "group": feature.group,
            "predicted_ab": feature.predicted,
            "label_stats": label_stats,
            "ab_diff": ab_diff,
            "omni_test": omni_test,
            "omni_stat": omni_stat,
            "omni_p": omni_p,
            "omni_p_bonf": stats.bonferroni(omni_p, n_features),
            "ab_test": ab_test,
            "ab_stat": ab_stat,
            "ab_p": ab_p,
            "ab_p_bonf": stats.bonferroni(ab_p, n_features),
            "effect_name": effect_name,
            "effect_size": effect_size,
            "n_a": na,
            "n_b": nb,
            "is_conditional": is_conditional,
        })

    return {
        "labels": list(labels),
        "pairwise": tuple(pairwise),
        "n_features": n_features,
        "features": results,
    }

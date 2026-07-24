"""
Created by davan (with Claude assistance)
7/23/26

Report writers for rates_by_label results: the three LaTeX tables and the
JSON summary exactly as the original analysis wrote them (byte-identical
formatting), figures behind the [viz] extra, and the per-example TSV with
the topic column fixed (deviation D-4).

All table/JSON writers take the results object returned by
analysis.rates_by_label and a destination path.
"""

import json
import os

from lexfeat import registry
from lexfeat.corpus import clean_rating, get_challenge, get_conv_id, get_topic
from lexfeat.features import clean_text
from lexfeat.stats import sig_stars


def _escape(display):
    return display.replace("%", "\\%").replace("&", "\\&")


def write_feature_definitions_tex(res: dict, path: str) -> None:
    """Feature/group/type/prediction table (paper Table 5 skeleton)."""
    results = res["features"]
    with open(path, "w") as f:
        f.write("\\begin{table}[t]\n")
        f.write("\\centering\n")
        f.write("\\small\n")
        f.write("\\caption{Linguistic feature definitions for expanded analysis.}\n")
        f.write("\\label{tab:expanded-feature-definitions}\n")
        f.write("\\begin{tabular}{llll}\n")
        f.write("\\toprule\n")
        f.write("Group & Feature & Type & Predicted A--B \\\\\n")
        f.write("\\midrule\n")
        current_group = None
        for r in results:
            group = r["group"]
            if group != current_group:
                if current_group is not None:
                    f.write("\\midrule\n")
                current_group = group
            ftype = "Binary" if r["is_binary"] else "Continuous"
            display = _escape(r["display"])
            pred = r["predicted_ab"].replace(">", "$>$").replace("<", "$<$")
            f.write(f"{group} & {display} & {ftype} & {pred} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")


def write_feature_rates_tex(res: dict, path: str) -> None:
    """Rates/means by label with the pairwise difference (paper Table 4)."""
    results = res["features"]
    labels = res["labels"]
    with open(path, "w") as f:
        f.write("\\begin{table}[t]\n")
        f.write("\\centering\n")
        f.write("\\small\n")
        f.write("\\caption{Linguistic feature rates by response quality label (expanded).}\n")
        f.write("\\label{tab:expanded-feature-rates}\n")
        f.write("\\begin{tabular}{lrrrrrr}\n")
        f.write("\\toprule\n")
        f.write("Feature & A & B & C & D & A--B & Sig. \\\\\n")
        f.write("\\midrule\n")
        current_group = None
        for r in results:
            if r["group"] != current_group:
                if current_group is not None:
                    f.write("\\midrule\n")
                current_group = r["group"]
            fmt = r["fmt"]
            vals = [fmt.format(r["label_stats"][lab]) for lab in labels]
            if r["is_binary"]:
                ab_str = f"{r['ab_diff']:+.1%}"
            else:
                ab_str = f"{r['ab_diff']:+.3f}"
            sig = sig_stars(r["ab_p_bonf"])
            display = _escape(r["display"])
            f.write(f"{display} & {vals[0]} & {vals[1]} & {vals[2]} & {vals[3]} "
                    f"& {ab_str} & {sig} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")


def write_significance_tex(res: dict, path: str) -> None:
    """Omnibus and pairwise test statistics table (paper Table 6)."""
    results = res["features"]
    with open(path, "w") as f:
        f.write("\\begin{table}[t]\n")
        f.write("\\centering\n")
        f.write("\\footnotesize\n")
        f.write("\\caption{Statistical tests for expanded linguistic features. "
                "$p$-values are Bonferroni-corrected across all features.}\n")
        f.write("\\label{tab:expanded-significance}\n")
        f.write("\\begin{tabular}{lllrlllrl}\n")
        f.write("\\toprule\n")
        f.write("Feature & Omni. & Stat & $p_{\\text{Bonf}}$ & Sig. "
                "& A--B & Stat & $p_{\\text{Bonf}}$ & Effect \\\\\n")
        f.write("\\midrule\n")
        for r in results:
            display = _escape(r["display"])
            omni_test = "$\\chi^2$" if r["omni_test"] == "chi2" else "K-W"
            ab_test = "$\\chi^2$" if r["ab_test"] == "chi2" else "M-W"
            eff_str = f"{r['effect_size']:+.3f}"
            f.write(f"{display} & {omni_test} & {r['omni_stat']:.1f} "
                    f"& {r['omni_p_bonf']:.4f} & {sig_stars(r['omni_p_bonf'])} "
                    f"& {ab_test} & {r['ab_stat']:.1f} & {r['ab_p_bonf']:.4f} "
                    f"& {eff_str} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")


def write_feature_summary_json(res: dict, path: str) -> None:
    """The per-feature JSON summary, serialized exactly as the original."""
    summary = []
    for r in res["features"]:
        summary.append({
            "feature": r["key"],
            "display_name": r["display"],
            "group": r["group"],
            "is_binary": r["is_binary"],
            "predicted_ab": r["predicted_ab"],
            "rates": r["label_stats"],
            "ab_diff": r["ab_diff"],
            "omnibus_test": r["omni_test"],
            "omnibus_stat": round(r["omni_stat"], 4),
            "omnibus_p": r["omni_p"],
            "omnibus_p_bonferroni": r["omni_p_bonf"],
            "ab_test": r["ab_test"],
            "ab_stat": round(r["ab_stat"], 4),
            "ab_p": r["ab_p"],
            "ab_p_bonferroni": r["ab_p_bonf"],
            "effect_size_name": r["effect_name"],
            "effect_size": round(r["effect_size"], 4),
        })
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)


def write_figures(res: dict, output_dir: str) -> None:
    """The three analysis figures; degrades to a warning without [viz]."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("WARNING: matplotlib not installed. Skipping figure generation.")
        print("  Install with: pip install 'lexical-feature-extraction[viz]'")
        return

    results = res["features"]
    labels_order = res["labels"]
    palette = ["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"]
    colors = {lab: palette[i % len(palette)] for i, lab in enumerate(labels_order)}

    # ── Figure 1a: Binary features (rates) ──
    binary_results = [r for r in results if r["is_binary"]]

    _fig, ax = plt.subplots(figsize=(6.5, 4.5))
    n_feat = len(binary_results)
    x = range(n_feat)
    width = 0.2
    for i, lab in enumerate(labels_order):
        vals = [r["label_stats"][lab] for r in binary_results]
        ax.bar([xi + i * width for xi in x], vals, width, label=lab, color=colors[lab])
    ax.set_xticks([xi + 1.5 * width for xi in x])
    ax.set_xticklabels([r["display"] for r in binary_results],
                       rotation=30, ha="right", fontsize=11)
    ax.set_ylabel("Rate", fontsize=12)
    ax.set_title("Binary Features by Quality Label", fontsize=13)
    ax.tick_params(axis="y", labelsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig_linguistic_features_expanded.pdf"),
                bbox_inches="tight")
    plt.close()

    # ── Figure 1b: Continuous features (means) ──
    continuous_results = [r for r in results if not r["is_binary"]]

    _fig, ax = plt.subplots(figsize=(6.5, 4.5))
    n_feat = len(continuous_results)
    x = range(n_feat)
    for i, lab in enumerate(labels_order):
        vals = []
        for r in continuous_results:
            v = r["label_stats"][lab]
            if r["key"] == "n_words":
                v = v / 10.0
            vals.append(v)
        ax.bar([xi + i * width for xi in x], vals, width, label=lab, color=colors[lab])
    ax.set_xticks([xi + 1.5 * width for xi in x])
    cont_names_display = [
        r["display"] + " (/10)" if r["key"] == "n_words" else r["display"]
        for r in continuous_results
    ]
    ax.set_xticklabels(cont_names_display, rotation=30, ha="right", fontsize=11)
    ax.set_ylabel("Mean value", fontsize=12)
    ax.set_title("Continuous Features by Quality Label", fontsize=13)
    ax.tick_params(axis="y", labelsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig_linguistic_features_expanded_2.pdf"),
                bbox_inches="tight")
    plt.close()

    # ── Figure 2: A-B gap chart sorted by magnitude ──
    _fig, ax = plt.subplots(figsize=(6.5, 9))

    sorted_results = sorted(
        results,
        key=lambda r: abs(r["ab_diff"] / 10.0 if r["key"] == "n_words" else r["ab_diff"]),
    )
    names = [r["display"] + " (/10)" if r["key"] == "n_words" else r["display"]
             for r in sorted_results]
    diffs = [r["ab_diff"] / 10.0 if r["key"] == "n_words" else r["ab_diff"]
             for r in sorted_results]
    sigs = [r["ab_p_bonf"] < 0.05 for r in sorted_results]

    bar_colors = ["#2ca02c" if d > 0 else "#d62728" for d in diffs]
    edge_colors = ["black" if s else "none" for s in sigs]
    linewidths = [1.5 if s else 0 for s in sigs]

    ax.barh(range(len(names)), diffs, color=bar_colors,
            edgecolor=edge_colors, linewidth=linewidths)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlabel("A - B difference (positive = A higher)", fontsize=12)
    ax.set_title("A vs. B Gap by Feature (sorted by magnitude)", fontsize=13)
    ax.tick_params(axis="x", labelsize=11)
    ax.axvline(x=0, color="black", linewidth=0.8)
    ax.grid(axis="x", alpha=0.3)

    for i in range(1, len(sorted_results)):
        if sorted_results[i]["group"] != sorted_results[i - 1]["group"]:
            ax.axhline(y=i - 0.5, color="gray", linewidth=0.5, linestyle="--", alpha=0.4)

    for i, (d, s) in enumerate(zip(diffs, sigs)):
        if s:
            offset = 0.005 if d >= 0 else -0.005
            ha = "left" if d >= 0 else "right"
            ax.text(d + offset, i, "*", fontsize=11, va="center", ha=ha, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig_ab_gap_expanded.pdf"), bbox_inches="tight")
    plt.close()


# Per-example TSV feature columns, in the original's display order. Boolean
# features are written 0/1, floats rounded to 4 places, None as "".
FEATURE_COLUMNS = [
    "n_words", "n_sentences", "n_questions",
    "has_question", "starts_with_ack", "has_user_engage", "has_you_ref",
    "has_opinion", "has_formulaic", "has_citation", "has_exclamation",
    "has_hedge", "n_hedges",
    "has_emphasizer", "n_emphasizers",
    "hedge_ratio",
    "has_discourse_marker", "n_discourse_markers",
    "n_first_person", "n_second_person", "self_ratio",
    "content_ratio", "ttr",
    "pm_density", "interactivity", "question_density",
]

BOOLEAN_FEATURES = {
    "has_question", "starts_with_ack", "has_user_engage", "has_you_ref",
    "has_opinion", "has_formulaic", "has_citation", "has_exclamation",
    "has_hedge", "has_emphasizer", "has_discourse_marker",
}


def write_per_example_tsv(data: list, path: str, profile) -> None:
    """One row per response candidate with metadata and all feature columns.

    data is the Athena corpus record list (see lexfeat.corpus). The topic
    column uses corpus.get_topic — the original script read a _topic field
    it never set, leaving the column empty (deviation D-4, fixed here).
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    extras = [registry.get("n_questions"), registry.get("n_discourse_markers")]

    example_rows = []
    for d in data:
        conv_id = get_conv_id(d) or ""
        topic = get_topic(d)
        user_text = str(d.get("this_turn_text", "") or "")
        rating = clean_rating(d.get("rating"))
        sgc = get_challenge(d)

        context_parts = []
        for turn in d.get("history_turns", []):
            context_parts.append(turn["user_text"] + " [EOT]")
            context_parts.append(" [EOT] ")
            context_parts.append(clean_text(turn["athena_resp"]) + " [EOT]")
        context_text = " ".join(context_parts)

        for c in d.get("response_candidates", []):
            label = c.get("label")
            if not label:
                continue
            cand_text = c.get("candidate_text", "")
            rg_name = c.get("candidate_rg_name", "")
            cleaned = clean_text(cand_text)
            ctx = {}
            feats = {f.id: f.fn(cleaned, ctx) for f in profile.features}
            for f in extras:
                feats[f.id] = f.fn(cleaned, ctx)
            chosen = 1 if c.get("chosen_by_heuristic_ranker") else 0

            row = {
                "conv_id": conv_id,
                "sgc": sgc,
                "topic": topic,
                "conv_rating": rating if rating is not None else "",
                "user_text": context_text + clean_text(user_text),
                "rg_name": rg_name,
                "label": label,
                "chosen_by_heuristic": chosen,
                "response_text": cleaned[:500],
            }
            for key in FEATURE_COLUMNS:
                val = feats[key]
                if key in BOOLEAN_FEATURES:
                    row[key] = int(val)
                elif val is None:
                    row[key] = ""
                elif isinstance(val, float):
                    row[key] = round(val, 4)
                else:
                    row[key] = val
            example_rows.append(row)

    tsv_headers = [
        "conv_id", "sgc", "topic", "conv_rating", "user_text", "rg_name",
        "label", "chosen_by_heuristic", "response_text",
    ] + FEATURE_COLUMNS

    with open(path, "w") as f:
        f.write("\t".join(tsv_headers) + "\n")
        for row in example_rows:
            vals = []
            for h in tsv_headers:
                v = row[h]
                if isinstance(v, str):
                    v = v.replace("\t", " ").replace("\n", " ").replace("\r", "")
                vals.append(str(v))
            f.write("\t".join(vals) + "\n")

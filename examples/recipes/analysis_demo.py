"""
Created by davan (with Claude assistance)
7/23/26

Analysis demo: the full rates-by-label pipeline over the committed
synthetic corpus — the same pipeline that produced the paper's Tables 4
and 6, showing a real A/B gap end to end. Writes tables and the JSON
summary to ./analysis_demo_out. Runnable with committed data only:
python analysis_demo.py
"""

import json
import os

from lexfeat import analysis, registry, report
from lexfeat.stats import sig_stars

HERE = os.path.dirname(__file__) or "."
CORPUS = os.path.join(HERE, "..", "synthetic", "corpus.jsonl")
OUT = os.path.join(HERE, "analysis_demo_out")


def main():
    prof = registry.profile("iva2026")
    with open(CORPUS) as fin:
        records = [json.loads(line) for line in fin]

    res = analysis.rates_by_label(records, prof)

    os.makedirs(OUT, exist_ok=True)
    report.write_feature_definitions_tex(res, os.path.join(OUT, "feature_definitions_table.tex"))
    report.write_feature_rates_tex(res, os.path.join(OUT, "feature_rates_table.tex"))
    report.write_significance_tex(res, os.path.join(OUT, "significance_tests_table.tex"))
    report.write_feature_summary_json(res, os.path.join(OUT, "feature_summary.json"))
    report.write_figures(res, OUT)

    print(f"{'feature':<22} {'A':>7} {'B':>7} {'A-B':>8}  sig")
    for r in res["features"]:
        a, b = r["label_stats"]["A"], r["label_stats"]["B"]
        print(f"{r['key']:<22} {a:>7.3f} {b:>7.3f} {r['ab_diff']:>+8.3f}  "
              f"{sig_stars(r['ab_p_bonf'])}")
    print(f"\nOutputs written to {OUT}")


if __name__ == "__main__":
    main()

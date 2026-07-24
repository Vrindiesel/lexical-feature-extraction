"""
Created by davan (with Claude assistance)
7/23/26

MAINTAINER-ONLY TOOL. Verifies that this library reproduces the published
IVA 2026 numbers exactly. It requires the private Athena annotated corpus,
which does not ship with this repository — for everyone else this file is
the executable provenance record of how the published feature_summary was
produced.

Runs the ported pipeline on the UNFILTERED corpus (matching the original
run — deviation D-1) and diffs every value of the resulting summary against
reference/feature_summary.iva2026.json at the serialized precision, with
exact equality and no tolerance: the ported writer replicates the
original's rounding and serialization, so any difference is real drift.
Exits nonzero on any mismatch and prints a per-key diff.

Usage:
  python tools/verify_published_numbers.py \
      --corpus /path/to/examples.norm.json \
      --reference reference/feature_summary.iva2026.json
"""

import argparse
import json
import os
import sys
import tempfile
import time

from lexfeat import analysis, corpus, registry, report


def compute_summary(corpus_path):
    """Run the full ported pipeline, unfiltered, and return the summary."""
    data = corpus.load_athena_norm(corpus_path)
    records = corpus.labeled_candidates(data)
    prof = registry.profile("iva2026")
    res = analysis.rates_by_label(records, prof)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = os.path.join(tmpdir, "summary.json")
        report.write_feature_summary_json(res, tmp_path)
        with open(tmp_path) as fin:
            return json.load(fin), len(records)


def diff_summaries(computed, reference):
    """Compare value for value; returns a list of (feature, key, ref, got)."""
    diffs = []
    ref_by_feature = {e["feature"]: e for e in reference}
    comp_by_feature = {e["feature"]: e for e in computed}

    for feature, ref_e in ref_by_feature.items():
        if feature not in comp_by_feature:
            diffs.append((feature, "<missing>", "present", "absent"))
            continue
        comp_e = comp_by_feature[feature]
        for key in ref_e:
            if key not in comp_e:
                diffs.append((feature, key, ref_e[key], "<absent>"))
            elif comp_e[key] != ref_e[key]:
                diffs.append((feature, key, ref_e[key], comp_e[key]))
        for key in comp_e:
            if key not in ref_e:
                diffs.append((feature, key, "<absent>", comp_e[key]))
    for feature in comp_by_feature:
        if feature not in ref_by_feature:
            diffs.append((feature, "<extra>", "absent", "present"))
    return diffs


def main():
    parser = argparse.ArgumentParser(description="Verify published IVA 2026 numbers.")
    parser.add_argument("--corpus", required=True,
                        help="Path to the private examples.norm.json corpus.")
    parser.add_argument("--reference", required=True,
                        help="Path to reference/feature_summary.iva2026.json.")
    args = parser.parse_args()

    with open(args.reference) as fin:
        reference = json.load(fin)["feature_summary"]

    print(f"Running ported pipeline on {args.corpus} (unfiltered, per D-1)...")
    t0 = time.time()
    computed, n_records = compute_summary(args.corpus)
    elapsed = time.time() - t0
    print(f"Extracted and analyzed {n_records} candidates in {elapsed:.1f}s")

    diffs = diff_summaries(computed, reference)
    if diffs:
        print(f"\nFAIL: {len(diffs)} value(s) differ from the published reference:")
        for feature, key, ref, got in diffs:
            print(f"  {feature}.{key}: reference={ref!r} computed={got!r}")
        sys.exit(1)

    n_values = sum(len(e) for e in reference)
    print(f"\nPASS: all {n_values} values across {len(reference)} features "
          f"match the published reference exactly.")


if __name__ == "__main__":
    main()

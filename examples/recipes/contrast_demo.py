"""
Created by davan (with Claude assistance)
7/23/26

Contrast demo: classify the paper's Figure 3 A/B response pairs (from
examples/paper_examples.jsonl) into contrast types. Runnable with
committed data only: python contrast_demo.py
"""

import json
import os

from lexfeat import registry
from lexfeat.contrast import classify_pair

EXAMPLES = os.path.join(os.path.dirname(__file__) or ".", "..", "paper_examples.jsonl")

# Figure 3 A/B pairs by whitelist id
PAIRS = [("W24", "W25"), ("W27", "W28"), ("W30", "W31"),
         ("W33", "W34"), ("W36", "W37"), ("W39", "W40")]


def main():
    prof = registry.profile("iva2026")
    with open(EXAMPLES) as fin:
        entries = {e["id"]: e for e in map(json.loads, fin) if "id" in e}

    for a_id, b_id in PAIRS:
        a, b = entries[a_id], entries[b_id]
        result = classify_pair(a["text"], b["text"], prof)
        print(f"{a_id}/{b_id}: {result['contrast_type']} "
              f"(priority {result['priority']})")
        print(f"  A: {a['text'][:70]}")
        print(f"  B: {b['text'][:70]}")
        print(f"  differing binary features: {', '.join(result['key_differences'])}\n")


if __name__ == "__main__":
    main()

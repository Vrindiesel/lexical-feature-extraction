"""
Created by davan (with Claude assistance)
7/23/26

Extraction demo: run the iva2026 profile over the paper's published
examples (examples/paper_examples.jsonl) and print a compact feature view.
Runnable with committed data only: python extract_demo.py
"""

import json
import os

from lexfeat import registry

EXAMPLES = os.path.join(os.path.dirname(__file__) or ".", "..", "paper_examples.jsonl")

SHOW = ["has_question", "starts_with_ack", "has_user_engage", "has_formulaic",
        "has_hedge", "n_words", "interactivity"]


def main():
    prof = registry.profile("iva2026")
    with open(EXAMPLES) as fin:
        entries = [json.loads(line) for line in fin]
    entries = [e for e in entries if e.get("record_type") != "provenance"]

    print(f"{'id':<5} {'label':<6} " + " ".join(f"{k:<16}" for k in SHOW))
    for e in entries[:20]:
        feats = prof.extract(e["text"])
        row = " ".join(f"{feats[k]!s:<16}" for k in SHOW)
        print(f"{e['id']:<5} {e['label'] or '-':<6} {row}")
    print(f"\n({len(entries)} paper examples available; showing 20)")


if __name__ == "__main__":
    main()

"""
Created by davan (with Claude assistance)
7/23/26

T6 — synthetic golden run: the committed synthetic corpus regenerates
byte-identically from its seed, the full analysis pipeline over it equals
the committed golden summary, and the demo shows a real A/B gap.
"""

import importlib.util
import json
import os

import pytest

SYNTH_DIR = os.path.join(os.path.dirname(__file__), "..", "examples", "synthetic")


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "synth_generate", os.path.join(SYNTH_DIR, "generate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def corpus_records():
    with open(os.path.join(SYNTH_DIR, "corpus.jsonl")) as fin:
        return [json.loads(line) for line in fin]


def test_corpus_regenerates_byte_identically():
    gen = _load_generator()
    regenerated = "\n".join(json.dumps(r) for r in gen.build_corpus()) + "\n"
    with open(os.path.join(SYNTH_DIR, "corpus.jsonl")) as fin:
        committed = fin.read()
    assert regenerated == committed


def test_golden_summary_matches(tmp_path, corpus_records):
    from lexfeat import analysis, registry, report

    prof = registry.profile("iva2026")
    res = analysis.rates_by_label(corpus_records, prof)
    out = tmp_path / "summary.json"
    report.write_feature_summary_json(res, str(out))
    recomputed = json.loads(out.read_text())
    with open(os.path.join(SYNTH_DIR, "golden_summary.json")) as fin:
        golden = json.load(fin)
    assert recomputed == golden


def test_ab_gap_is_real(corpus_records):
    with open(os.path.join(SYNTH_DIR, "golden_summary.json")) as fin:
        golden = json.load(fin)
    by_feature = {e["feature"]: e for e in golden}

    # A-favored features are higher for A and significant after correction
    for feat in ["has_question", "starts_with_ack", "interactivity"]:
        e = by_feature[feat]
        assert e["rates"]["A"] > e["rates"]["B"], feat
        assert e["ab_p_bonferroni"] < 0.05, feat

    # B-favored features run the other way
    for feat in ["has_formulaic", "has_opinion", "has_hedge"]:
        e = by_feature[feat]
        assert e["rates"]["B"] > e["rates"]["A"], feat
        assert e["ab_p_bonferroni"] < 0.05, feat

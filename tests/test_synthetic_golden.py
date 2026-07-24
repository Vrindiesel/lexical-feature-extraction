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


def assert_deep_close(a, b, path=""):
    """Exact equality except floats, which get a last-ulp-scale tolerance.

    Python 3.12 switched builtin sum() to compensated summation, so the
    unrounded means and p-values in the golden file (generated on 3.9)
    drift in the final bit on newer interpreters.
    """
    if isinstance(a, float) and isinstance(b, float):
        assert a == pytest.approx(b, rel=1e-9, abs=1e-12), path
    elif isinstance(a, dict) and isinstance(b, dict):
        assert a.keys() == b.keys(), path
        for k in a:
            assert_deep_close(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        assert len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            assert_deep_close(x, y, f"{path}[{i}]")
    else:
        assert type(a) is type(b) and a == b, path


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
    assert_deep_close(recomputed, golden)


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

"""
Created by davan (with Claude assistance)
7/23/26

T5 — published-constant spot checks: the shipped reference summary carries
the paper's Table 4/6 values (has_question rates, chi-square, Cramer's V,
interactivity index). Consistency of the shipped artifact; no corpus needed.
"""

import json
import os

import pytest

REF_PATH = os.path.join(os.path.dirname(__file__), "..", "reference",
                        "feature_summary.iva2026.json")


@pytest.fixture(scope="module")
def reference():
    with open(REF_PATH) as fin:
        return json.load(fin)


def _entry(reference, feature):
    return next(e for e in reference["feature_summary"] if e["feature"] == feature)


def test_provenance_present(reference):
    prov = reference["_provenance"]
    assert prov["source_commit"] == "e76c20f"
    assert "unfiltered" in prov["corpus_note"]


def test_has_question_published_values(reference):
    e = _entry(reference, "has_question")
    # Paper Table 4: A = 59.5%, B = 46.2%
    assert f"{e['rates']['A']:.1%}" == "59.5%"
    assert f"{e['rates']['B']:.1%}" == "46.2%"
    # Paper Table 6: A-B chi2 = 144.7, Cramer's V = .112
    assert round(e["ab_stat"], 1) == 144.7
    assert round(e["effect_size"], 3) == 0.112
    assert e["ab_test"] == "chi2"
    assert e["effect_size_name"] == "Cramer_V"


def test_interactivity_published_values(reference):
    e = _entry(reference, "interactivity")
    # Paper Table 4: interactivity index A = .414, B = .312
    assert round(e["rates"]["A"], 3) == 0.414
    assert round(e["rates"]["B"], 3) == 0.312


def test_all_25_features_present(reference):
    from lexfeat import registry

    prof = registry.profile("iva2026")
    ref_order = [e["feature"] for e in reference["feature_summary"]]
    assert ref_order == [f.id for f in prof.features]

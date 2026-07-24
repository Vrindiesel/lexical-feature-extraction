"""
Created by davan (with Claude assistance)
7/23/26

Athena examples.norm.json loader and RG filters.

Maintainer-facing: the Athena annotated corpus is private and does not ship
with this repository (see the README data statement). These functions are
public so the analysis pipeline that produced the paper is fully inspectable
and rerunnable by the maintainer; they are useful to others only as format
documentation. Each corpus record is a dialogue turn with a
response_candidates list ({label, candidate_text, candidate_rg_name,
chosen_by_heuristic_ranker}), this_turn_text, history_turns
({user_text, athena_resp}), conversation_id/conv_id, rating,
creation_date_time, and topic fields (topic_constraint/last_turn_topic).
"""

import json
from typing import Optional

# The paper's Table 3 exclusion set: three all-D generators removed from the
# label-distribution analysis (1,612 responses). Note: this is NOT the same
# exclusion set as the per-challenge figure script, which excludes ap_nrg
# instead of CONTROLLED_POLICY_DRIVEN_NRG.
EXCLUDED_RGS_TABLE3 = frozenset({"ap_atm5b", "ap_atm20b", "CONTROLLED_POLICY_DRIVEN_NRG"})


def load_athena_norm(path: str) -> list:
    """Load an examples.norm.json corpus file: a JSON list of turn records."""
    with open(path) as fin:
        return json.load(fin)


def labeled_candidates(data: list) -> list:
    """Flatten corpus records into analysis records, preserving file order.

    Returns a list of {"label", "text", "rg"} dicts, one per response
    candidate — the record shape analysis.rates_by_label consumes.
    Candidates without a label are kept (the analysis skips them), so
    counts match the original pipeline exactly.
    """
    records = []
    for d in data:
        for c in d.get("response_candidates", []):
            records.append({
                "label": c.get("label"),
                "text": c.get("candidate_text", ""),
                "rg": c.get("candidate_rg_name", ""),
            })
    return records


def filter_rgs(data: list, excluded=None) -> list:
    """Return corpus records with candidates from excluded RGs removed.

    excluded defaults to EXCLUDED_RGS_TABLE3, the paper's Table 3 filter.
    Records are shallow-copied; candidate lists are rebuilt.
    """
    if excluded is None:
        excluded = EXCLUDED_RGS_TABLE3
    filtered = []
    for d in data:
        kept = [c for c in d.get("response_candidates", [])
                if c.get("candidate_rg_name") not in excluded]
        new_d = dict(d)
        new_d["response_candidates"] = kept
        filtered.append(new_d)
    return filtered


def get_conv_id(instance: dict):
    return instance.get("conversation_id") or instance.get("conv_id")


def clean_rating(r) -> Optional[float]:
    if r is None:
        return None
    s = str(r).replace("*", "")
    try:
        return float(s)
    except ValueError:
        return None


def get_challenge(instance: dict) -> str:
    """Attribute an instance to an Alexa Prize challenge by creation_date_time."""
    dt = instance.get("creation_date_time", "")
    if dt.startswith("2020"):
        return "SGC3"
    elif dt.startswith("2021"):
        return "SGC4"
    elif dt.startswith("2023"):
        return "SGC5"
    return "unknown"


def get_topic(instance: dict) -> str:
    """Turn topic: topic_constraint, else last_turn_topic, else "unknown".

    This is the derivation the original per-example TSV intended (its
    _topic field was never populated in the expanded-features script —
    deviation D-4, fixed here).
    """
    return instance.get("topic_constraint") or instance.get("last_turn_topic") or "unknown"

"""
Created by davan (with Claude assistance)
7/23/26

A/B contrast classification and key-difference reporting over profile
features.

classify_contrast, key_differences, and the pair-quality filters are ported
behaviorally verbatim from the paper's A/B pair extraction (the source of
its Figure 3 material); classify_pair rewires them over Profile.extract so
one extractor serves the whole library. Note: the original pair-extraction
script ran with slightly drifted cue lists (missing "kinda" and
"kinda like" — deviation D-3); the canonical iva2026 lists are used here,
which affected no published number.
"""

from lexfeat.features import clean_text

# Binary features considered when listing pair differences, in the
# original's order.
BINARY_KEYS = [
    "has_question", "starts_with_ack", "has_user_engage",
    "has_you_ref", "has_exclamation", "has_opinion",
    "has_formulaic", "has_citation",
    "has_hedge", "has_emphasizer", "has_discourse_marker",
]


def key_differences(a_feats: dict, b_feats: dict) -> list:
    """Return list of feature names where A and B differ (binary features)."""
    return [k.replace("has_", "").replace("starts_with_", "")
            for k in BINARY_KEYS if a_feats[k] != b_feats[k]]


def classify_contrast(a_feats: dict, b_feats: dict) -> tuple:
    """Classify the A/B pair into a contrast type. Returns (type, priority)."""
    # Formulaic opening (B) vs natural opening (A)
    if b_feats["has_formulaic"] and not a_feats["has_formulaic"]:
        return "formulaic_vs_natural", 1

    # Ack + question vs no-ack info delivery
    if (a_feats["starts_with_ack"] and a_feats["has_question"] and
            not b_feats["starts_with_ack"] and not b_feats["has_question"]):
        return "ack_question_vs_info", 2

    # Question vs no question
    if a_feats["has_question"] and not b_feats["has_question"]:
        return "question_vs_no_question", 3

    # Exclamation/engagement vs flat
    if ((a_feats["has_exclamation"] or a_feats["has_user_engage"]) and
            not b_feats["has_exclamation"] and not b_feats["has_user_engage"]):
        return "engagement_vs_flat", 4

    # Self-oriented (B high self-ratio) vs other-oriented (A low self-ratio)
    if (a_feats["self_ratio"] is not None and b_feats["self_ratio"] is not None
            and b_feats["self_ratio"] > 0.7 and a_feats["self_ratio"] < 0.4):
        return "self_vs_other_oriented", 5

    # Brief + interactive vs long + monologic
    if (a_feats["n_words"] < 20 and a_feats["has_question"] and
            b_feats["n_words"] > 30):
        return "brief_interactive_vs_long", 6

    # Hedge/emphasizer contrast
    if (a_feats["has_hedge"] and not b_feats["has_hedge"] and
            a_feats["has_emphasizer"] and not b_feats["has_emphasizer"]):
        return "pragmatic_rich_vs_bare", 7

    # Ack opening only
    if a_feats["starts_with_ack"] and not b_feats["starts_with_ack"]:
        return "ack_vs_no_ack", 8

    # Discourse marker contrast
    if a_feats["has_discourse_marker"] and not b_feats["has_discourse_marker"]:
        return "dm_vs_no_dm", 9

    diffs = key_differences(a_feats, b_feats)
    if diffs:
        return "other_contrast", 10

    return "no_clear_contrast", 99


def is_clean_text(text: str) -> bool:
    """Pair-quality filter for candidate responses."""
    if len(text) < 5:
        return False
    if text.count("...") > 2:
        return False
    return len(text.split()) <= 60


def is_clean_user_utterance(text: str) -> bool:
    """Pair-quality filter for the user turn preceding a pair."""
    if not text or len(text.strip()) < 2:
        return False
    return len(text.split()) <= 25


def classify_pair(a_text: str, b_text: str, profile) -> dict:
    """Extract features for both sides and classify the contrast.

    Texts are SSML-stripped before extraction, matching the analysis layer.
    Returns a dict with both feature dicts, the contrast type/priority, and
    the differing binary features.
    """
    a_feats = profile.extract(clean_text(a_text))
    b_feats = profile.extract(clean_text(b_text))
    contrast_type, priority = classify_contrast(a_feats, b_feats)
    return {
        "a_feats": a_feats,
        "b_feats": b_feats,
        "contrast_type": contrast_type,
        "priority": priority,
        "key_differences": key_differences(a_feats, b_feats),
    }

"""
Created by davan (with Claude assistance)
7/23/26

T1 — quirk locks: one test per frozen behavioral quirk of the iva2026
extractor (see lexfeat.lexicons docstring). All strings are hand-written
for these tests; the published numbers embed each behavior.
"""

from lexfeat import registry

PROF = registry.profile("iva2026")


def test_quirk1_substring_matching():
    # "about" inside "roundabout" counts as a hedge
    feats = PROF.extract("The roundabout is closed.")
    assert feats["has_hedge"] is True
    assert feats["n_hedges"] == 1


def test_quirk2_ack_prefix_only():
    assert PROF.extract("Cool, that sounds fine.")["starts_with_ack"] is True
    # "cool" mid-utterance does not count
    assert PROF.extract("That was cool.")["starts_with_ack"] is False


def test_quirk2_dm_initial_prefix_and_double_count():
    feats = PROF.extract("i mean, it works.")
    assert feats["has_discourse_marker"] is True
    # "i mean" is in both DM lists, so it counts twice when initial
    n_dm = registry.get("n_discourse_markers")
    assert n_dm.fn("i mean, it works.", {}) == 2
    # non-initial "well" is not a discourse marker (not in the ANY list)
    assert PROF.extract("That went well")["has_discourse_marker"] is False


def test_quirk3_space_padded_pronouns():
    feats = PROF.extract("I told you.")
    assert feats["n_first_person"] == 1
    # "you." is blocked by the trailing period
    assert feats["n_second_person"] == 0
    assert feats["self_ratio"] == 1.0


def test_quirk4_so_intensifier_closed_list():
    assert PROF.extract("This is so good.")["n_emphasizers"] == 1
    # "strange" is not in the closed adjective list
    feats = PROF.extract("This is so strange.")
    assert feats["n_emphasizers"] == 0
    assert feats["has_emphasizer"] is False


def test_quirk5_conditional_none():
    feats = PROF.extract("Fine.")
    assert feats["hedge_ratio"] is None
    assert feats["self_ratio"] is None


def test_quirk6_sentence_segmentation():
    # trailing punctuation yields an extra empty segment
    assert PROF.extract("Hello there. Bye.")["n_sentences"] == 3
    assert PROF.extract("Hello there")["n_sentences"] == 1


def test_quirk7_multi_question():
    assert PROF.extract("What? Why?")["multi_question"] == 1
    assert PROF.extract("What now?")["multi_question"] == 0


def test_quirk8_interactivity_five_feature_mean():
    # all five components fire
    assert PROF.extract("Oh nice! Do you agree?")["interactivity"] == 1.0
    # only has_question fires
    assert PROF.extract("Will it rain today?")["interactivity"] == 1 / 5.0

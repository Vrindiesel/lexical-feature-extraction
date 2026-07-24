"""
Created by davan (with Claude assistance)
7/23/26

T4 — extractor spot checks: four paper examples (whitelist ids W24, W25,
W31, W33; all excerpts appear verbatim in the published paper, Figure 3)
with every feature value hand-computed. Expected floats are written as the
same division the extractor performs, so equality is exact.
"""

from lexfeat import registry

PROF = registry.profile("iva2026")

W24 = "Oh I think cats are magnificent! What do you like about them?"
W24_EXPECTED = {
    "has_question": True,
    "multi_question": 0,
    "has_user_engage": True,       # "what do you", "do you"
    "has_you_ref": True,
    "starts_with_ack": True,       # "oh"
    "has_exclamation": True,
    "has_opinion": True,           # "i think"
    "has_formulaic": False,
    "has_citation": False,
    "n_words": 12,
    "n_sentences": 3,              # "...magnificent!" / "...them?" / ""
    "has_hedge": True,
    "n_hedges": 2,                 # "about", "i think"
    "has_emphasizer": False,
    "n_emphasizers": 0,
    "hedge_ratio": 1.0,
    "has_discourse_marker": False,
    "self_ratio": 1 / 2,           # " i " vs " you "
    "n_first_person": 1,
    "n_second_person": 1,
    "content_ratio": 5 / 12,       # oh, think, cats, magnificent, like
    "ttr": 1.0,                    # 12 distinct words
    "pm_density": 2 / 12,
    "interactivity": 5 / 5.0,
    "question_density": 1 / 3,
}

W25 = (
    "I read online the other day this fact about cats. Outdoor cats are "
    "active both day and night, although they tend to be slightly more "
    "active at night."
)
W25_EXPECTED = {
    "has_question": False,
    "multi_question": 0,
    "has_user_engage": False,
    "has_you_ref": False,
    "starts_with_ack": False,
    "has_exclamation": False,
    "has_opinion": False,
    "has_formulaic": False,        # "i read online" is not "i read that"
    "has_citation": False,
    "n_words": 28,
    "n_sentences": 3,
    "has_hedge": True,
    "n_hedges": 1,                 # "about"
    "has_emphasizer": False,
    "n_emphasizers": 0,
    "hedge_ratio": 1.0,
    "has_discourse_marker": False,
    "self_ratio": 1.0,             # leading " i ", no second person
    "n_first_person": 1,
    "n_second_person": 0,
    "content_ratio": 18 / 28,      # function words: i, the, this, about,
    "ttr": 24 / 28,                #   are, and, they, to, be, at
    "pm_density": 1 / 28,          # duplicates: cats, day, night, active
    "interactivity": 0 / 5.0,
    "question_density": 0 / 3,
}

W31 = (
    "Hm, basketball? Oh yeah, alright. I've seen it online. It seemed kind "
    "of funny to me. But interesting. Do people enjoy it?"
)
W31_EXPECTED = {
    "has_question": True,
    "multi_question": 1,           # two "?"
    "has_user_engage": False,      # "do people", not "do you"
    "has_you_ref": False,
    "starts_with_ack": False,      # "hm" is not in ACK_STARTS
    "has_exclamation": False,
    "has_opinion": True,           # "to me"
    "has_formulaic": False,
    "has_citation": False,
    "n_words": 22,
    "n_sentences": 7,              # six [.!?]+ runs + trailing empty segment
    "has_hedge": True,
    "n_hedges": 1,                 # "kind of" ("it seemed" != "it seems")
    "has_emphasizer": False,
    "n_emphasizers": 0,
    "hedge_ratio": 1.0,
    "has_discourse_marker": False,  # "alright" is not utterance-initial
    "self_ratio": 1.0,             # " i'" only; "me." blocked by period
    "n_first_person": 1,
    "n_second_person": 0,
    "content_ratio": 14 / 22,      # function words: it x3, of, to, me,
    "ttr": 20 / 22,                #   but, do; duplicate: it x3
    "pm_density": 1 / 22,
    "interactivity": 1 / 5.0,      # has_question only
    "question_density": 2 / 7,
}

W33 = (
    "Sure! Here's something funny, a dog's nose print is unique, much like "
    "a person's fingerprint. Do you want to hear more?"
)
W33_EXPECTED = {
    "has_question": True,
    "multi_question": 0,
    "has_user_engage": True,       # "do you", "want to"
    "has_you_ref": True,
    "starts_with_ack": True,       # "sure"
    "has_exclamation": True,
    "has_opinion": False,
    "has_formulaic": True,         # "here's something"
    "has_citation": False,
    "n_words": 21,
    "n_sentences": 4,
    "has_hedge": False,
    "n_hedges": 0,
    "has_emphasizer": False,       # "something" does not match \bso\s+
    "n_emphasizers": 0,
    "hedge_ratio": None,           # no markers at all
    "has_discourse_marker": False,
    "self_ratio": 0 / 1,           # " you " only
    "n_first_person": 0,
    "n_second_person": 1,
    "content_ratio": 15 / 21,      # function words: a x2, is, do, you, to
    "ttr": 20 / 21,                # duplicate: a x2
    "pm_density": 0.0,
    "interactivity": 5 / 5.0,
    "question_density": 1 / 4,
}


def _check(text, expected):
    actual = PROF.extract(text)
    assert set(actual) == set(expected)
    for key, want in expected.items():
        got = actual[key]
        assert (got is None) == (want is None), key
        assert got == want, f"{key}: got {got!r}, want {want!r}"


def test_w24():
    _check(W24, W24_EXPECTED)


def test_w25():
    _check(W25, W25_EXPECTED)


def test_w31():
    _check(W31, W31_EXPECTED)


def test_w33():
    _check(W33, W33_EXPECTED)

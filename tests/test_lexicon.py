"""
Created by davan (with Claude assistance)
7/23/26

T2 — lexicon integrity: iva2026.v1.json equals the exact published cue
lists, literal for literal. Guards accidental edits to a frozen artifact.
"""

from lexfeat.lexicons import load_lexicon

LEX = load_lexicon("iva2026", 1)


def test_metadata():
    assert LEX["lexicon"] == "iva2026"
    assert LEX["version"] == 1
    assert LEX["frozen"] is True


def test_ack_starts():
    assert LEX["lists"]["ACK_STARTS"] == [
        "oh", "wow", "nice", "cool", "great", "awesome", "interesting",
        "huh", "ooh", "that's", "yeah", "right", "sure", "ok", "okay",
        "i see", "i know", "totally", "absolutely", "definitely",
    ]


def test_formulaic_openings():
    assert LEX["lists"]["FORMULAIC_OPENINGS"] == [
        "here is", "here's a fact", "here's something", "here's an",
        "did you know", "i found", "according to", "reportedly",
        "i read that", "here is a", "here's a piece",
    ]


def test_opinion_markers():
    assert LEX["lists"]["OPINION_MARKERS"] == [
        "i think", "i love", "i like", "i feel", "i believe",
        "to me", "in my opinion", "i'm wondering", "personally",
    ]


def test_user_engage():
    assert LEX["lists"]["USER_ENGAGE"] == [
        "what do you", "do you", "how about you", "have you",
        "would you", "are you", "want to", "can you tell me",
        "what's your", "what are your",
    ]


def test_citation_patterns():
    assert LEX["lists"]["CITATION_PATTERNS"] == [
        "according to", "wikipedia", "ranker.com", "reportedly",
        "sources say",
    ]


def test_hedges():
    assert LEX["lists"]["HEDGES"] == [
        "kind of", "sort of", "somewhat", "a little", "a bit",
        "pretty much", "more or less", "to some extent", "kinda",
        "around", "about", "roughly", "approximately",
        "almost", "nearly",
        "quite", "rather", "fairly", "relatively",
        "i think", "i guess", "i suppose", "i imagine",
        "i believe",
        "it seems", "it appears", "it looks like",
        "maybe", "perhaps", "possibly", "probably",
        "might", "could be",
    ]


def test_emphasizers():
    assert LEX["lists"]["EMPHASIZERS"] == [
        "really", "very",
        "totally", "absolutely", "completely", "definitely",
        "extremely", "incredibly", "truly", "literally",
        "actually", "basically", "obviously", "certainly",
        "clearly", "of course",
        "just",
        "even",
    ]


def test_so_intensifier_pattern():
    assert LEX["patterns"]["SO_INTENSIFIER_RE"] == (
        r"\bso\s+(good|great|cool|much|many|nice|funny|interesting|amazing|"
        r"awesome|bad|hard|weird|fun|cute|pretty|beautiful|long|far|close)\b"
    )


def test_discourse_markers_initial():
    assert LEX["lists"]["DISCOURSE_MARKERS_INITIAL"] == [
        "well", "so", "now", "anyway", "anyways",
        "alright", "hey", "look", "see",
        "i mean", "you know what",
    ]


def test_discourse_markers_any():
    assert LEX["lists"]["DISCOURSE_MARKERS_ANY"] == [
        "you know", "i mean",
        "or something", "or whatever",
        "and stuff", "and things", "and everything",
        "kind of like", "sort of like", "kinda like",
    ]


def test_person_lists():
    assert LEX["lists"]["FIRST_PERSON"] == [" i ", " i'", " my ", " me ", " mine ", " myself "]
    assert LEX["lists"]["SECOND_PERSON"] == [" you ", " your ", " yours ", " yourself "]


def test_function_words():
    # The source defines a set; the lexicon file serializes it sorted.
    literal = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after",
        "and", "but", "or", "nor", "not", "so", "yet",
        "if", "then", "that", "which", "who", "whom", "this", "these",
        "those", "it", "its", "i", "me", "my", "you", "your", "he",
        "she", "they", "we", "him", "her", "them", "us",
        "what", "when", "where", "how", "why",
        "up", "out", "about", "just", "also", "very", "really",
        "there", "here",
    }
    assert LEX["lists"]["FUNCTION_WORDS"] == sorted(literal)

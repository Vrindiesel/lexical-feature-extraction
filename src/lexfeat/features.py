"""
Created by davan (with Claude assistance)
7/23/26

Per-feature extractor functions and shared intermediates for the lexfeat
registry.

Every feature function has the signature (text, ctx): ctx is a per-response
dict of shared intermediates, populated once by _ensure_context on first use
and read by all features of the same response. The computations reproduce
the original IVA 2026 extractor exactly, including its quirks (see
lexfeat.lexicons for the list): substring matching, prefix rules, the
50-character discourse-marker window, space-padded pronoun counts, [.!?]+
sentence segmentation, and None for the conditional ratios.

Feature functions operate on the text they are given. SSML stripping is the
caller's job: apply clean_text first, exactly as the original pipeline
cleaned candidate text before computing features.
"""

import re

from lexfeat.lexicons import load_lexicon

_LEX = load_lexicon("iva2026", 1)

ACK_STARTS = _LEX["lists"]["ACK_STARTS"]
FORMULAIC_OPENINGS = _LEX["lists"]["FORMULAIC_OPENINGS"]
OPINION_MARKERS = _LEX["lists"]["OPINION_MARKERS"]
USER_ENGAGE = _LEX["lists"]["USER_ENGAGE"]
CITATION_PATTERNS = _LEX["lists"]["CITATION_PATTERNS"]
HEDGES = _LEX["lists"]["HEDGES"]
EMPHASIZERS = _LEX["lists"]["EMPHASIZERS"]
DISCOURSE_MARKERS_INITIAL = _LEX["lists"]["DISCOURSE_MARKERS_INITIAL"]
DISCOURSE_MARKERS_ANY = _LEX["lists"]["DISCOURSE_MARKERS_ANY"]
FIRST_PERSON = _LEX["lists"]["FIRST_PERSON"]
SECOND_PERSON = _LEX["lists"]["SECOND_PERSON"]
FUNCTION_WORDS = set(_LEX["lists"]["FUNCTION_WORDS"])
SO_INTENSIFIER_RE = re.compile(_LEX["patterns"]["SO_INTENSIFIER_RE"])


def clean_text(text: str) -> str:
    """Strip SSML / Amazon markup tags."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _ensure_context(text, ctx):
    """Populate ctx with the shared intermediates, once per response."""
    if "lower" in ctx:
        return ctx

    lower = text.lower()
    words = text.split()
    ctx["lower"] = lower
    ctx["words"] = words
    ctx["n_words"] = len(words)
    ctx["n_sentences"] = len(re.split(r"[.!?]+", text))
    ctx["n_questions"] = text.count("?")

    ctx["n_hedges"] = sum(1 for h in HEDGES if h in lower)
    n_emphasizers = sum(1 for e in EMPHASIZERS if e in lower)
    n_emphasizers += len(SO_INTENSIFIER_RE.findall(lower))
    ctx["n_emphasizers"] = n_emphasizers

    first_50 = lower[:50]
    ctx["has_dm_initial"] = any(first_50.startswith(dm) for dm in DISCOURSE_MARKERS_INITIAL)
    ctx["has_dm_any"] = any(dm in lower for dm in DISCOURSE_MARKERS_ANY)
    n_dm = sum(1 for dm in DISCOURSE_MARKERS_ANY if dm in lower)
    n_dm += sum(1 for dm in DISCOURSE_MARKERS_INITIAL if first_50.startswith(dm))
    ctx["n_discourse_markers"] = n_dm

    # Space padding for pronoun boundary matching
    padded = " " + lower + " "
    ctx["n_first_person"] = sum(padded.count(p) for p in FIRST_PERSON)
    ctx["n_second_person"] = sum(padded.count(p) for p in SECOND_PERSON)

    ctx["words_lower"] = [w.strip(".,!?;:'\"").lower() for w in words]
    return ctx


# ── Interactivity ────────────────────────────────────────────────────────────

def has_question(text, ctx):
    return "?" in text


def multi_question(text, ctx):
    _ensure_context(text, ctx)
    return 1 if ctx["n_questions"] > 1 else 0


def has_user_engage(text, ctx):
    _ensure_context(text, ctx)
    return any(m in ctx["lower"] for m in USER_ENGAGE)


def has_you_ref(text, ctx):
    _ensure_context(text, ctx)
    return bool(re.search(r"\b(you|your)\b", ctx["lower"]))


def n_questions(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_questions"]


# ── Acknowledgement / Expressiveness / Formulaicity ─────────────────────────

def starts_with_ack(text, ctx):
    _ensure_context(text, ctx)
    return any(ctx["lower"].startswith(a) for a in ACK_STARTS)


def has_exclamation(text, ctx):
    return "!" in text


def has_opinion(text, ctx):
    _ensure_context(text, ctx)
    return any(m in ctx["lower"] for m in OPINION_MARKERS)


def has_formulaic(text, ctx):
    _ensure_context(text, ctx)
    return any(m in ctx["lower"] for m in FORMULAIC_OPENINGS)


def has_citation(text, ctx):
    _ensure_context(text, ctx)
    return any(p in ctx["lower"] for p in CITATION_PATTERNS)


# ── Structural ───────────────────────────────────────────────────────────────

def n_words(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_words"]


def n_sentences(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_sentences"]


# ── Pragmatic force ──────────────────────────────────────────────────────────

def has_hedge(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_hedges"] > 0


def n_hedges(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_hedges"]


def has_emphasizer(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_emphasizers"] > 0


def n_emphasizers(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_emphasizers"]


def hedge_ratio(text, ctx):
    """Hedges over all markers; None when the response has no markers."""
    _ensure_context(text, ctx)
    total_he = ctx["n_hedges"] + ctx["n_emphasizers"]
    return ctx["n_hedges"] / total_he if total_he > 0 else None


# ── Discourse markers ────────────────────────────────────────────────────────

def has_discourse_marker(text, ctx):
    _ensure_context(text, ctx)
    return ctx["has_dm_initial"] or ctx["has_dm_any"]


def n_discourse_markers(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_discourse_markers"]


# ── Self/other orientation ───────────────────────────────────────────────────

def self_ratio(text, ctx):
    """First-person over all person references; None when there are none."""
    _ensure_context(text, ctx)
    total_person = ctx["n_first_person"] + ctx["n_second_person"]
    return ctx["n_first_person"] / total_person if total_person > 0 else None


def n_first_person(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_first_person"]


def n_second_person(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_second_person"]


# ── Information density ──────────────────────────────────────────────────────

def content_ratio(text, ctx):
    _ensure_context(text, ctx)
    n_content = sum(1 for w in ctx["words_lower"] if w and w not in FUNCTION_WORDS)
    return n_content / ctx["n_words"] if ctx["n_words"] > 0 else 0.0


def ttr(text, ctx):
    _ensure_context(text, ctx)
    cleaned_words = [w for w in ctx["words_lower"] if w]
    return len(set(cleaned_words)) / len(cleaned_words) if cleaned_words else 0.0


# ── Composites ───────────────────────────────────────────────────────────────

def pm_density(text, ctx):
    _ensure_context(text, ctx)
    pm_total = ctx["n_hedges"] + ctx["n_emphasizers"] + ctx["n_discourse_markers"]
    return pm_total / ctx["n_words"] if ctx["n_words"] > 0 else 0.0


def interactivity(text, ctx):
    """Mean of the five binary features listed in lexicon quirk 8."""
    _ensure_context(text, ctx)
    return sum([
        has_question(text, ctx),
        has_user_engage(text, ctx),
        has_you_ref(text, ctx),
        starts_with_ack(text, ctx),
        has_exclamation(text, ctx),
    ]) / 5.0


def question_density(text, ctx):
    _ensure_context(text, ctx)
    return ctx["n_questions"] / max(ctx["n_sentences"], 1)

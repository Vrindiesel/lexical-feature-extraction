"""
Created by davan (with Claude assistance)
7/23/26

Profile definitions. iva2026: the 25 features analyzed in the IVA 2026
paper, in Table 5 order, pinned to lexicon iva2026 v1 (frozen).
n_questions and n_discourse_markers are registered in the registry but sit
outside the profile's 25 analyzed features.
"""

from lexfeat import features, registry
from lexfeat.registry import Feature, Profile

# (id, display name, kind, group, predicted A-B) — carried over from the
# original FEATURE_SPEC, paper Table 5 order.
IVA2026_SPEC = [
    ("has_question", "Has question", "binary", "Interactivity", "A > B"),
    ("multi_question", "Multi-question", "binary", "Interactivity", "A > B"),
    ("has_user_engage", "User engagement", "binary", "Interactivity", "A > B"),
    ("has_you_ref", "You/your ref", "binary", "Interactivity", "A > B"),
    ("starts_with_ack", "Starts w/ ack", "binary", "Acknowledgement", "A > B"),
    ("has_exclamation", "Exclamation", "binary", "Expressiveness", "A > B"),
    ("has_opinion", "Opinion marker", "binary", "Expressiveness", "B > A"),
    ("has_formulaic", "Formulaic opening", "binary", "Formulaicity", "B > A"),
    ("has_citation", "Citation pattern", "binary", "Formulaicity", "n.s."),
    ("n_words", "Word count", "continuous", "Structural", "A < B"),
    ("n_sentences", "Sentence count", "continuous", "Structural", "n.s."),
    ("has_hedge", "Hedge presence", "binary", "Pragmatic Force", "A > B"),
    ("n_hedges", "Hedge count", "continuous", "Pragmatic Force", "A > B"),
    ("has_emphasizer", "Emphasizer presence", "binary", "Pragmatic Force", "A > B"),
    ("n_emphasizers", "Emphasizer count", "continuous", "Pragmatic Force", "A > B"),
    ("hedge_ratio", "Hedge-to-emph ratio", "continuous", "Pragmatic Force", "?"),
    ("has_discourse_marker", "Discourse marker", "binary", "Discourse Markers", "A > B"),
    ("self_ratio", "Self-orientation", "continuous", "Self/Other", "B > A"),
    ("n_first_person", "1st person count", "continuous", "Self/Other", "B > A"),
    ("n_second_person", "2nd person count", "continuous", "Self/Other", "A > B"),
    ("content_ratio", "Content word ratio", "continuous", "Info Density", "A < B"),
    ("ttr", "Type-token ratio", "continuous", "Info Density", "?"),
    ("pm_density", "Pragmatic marker dens.", "composite", "Composite", "A > B"),
    ("interactivity", "Interactivity index", "composite", "Composite", "A > B"),
    ("question_density", "Question density", "composite", "Composite", "A > B"),
]

# Registry features outside the profile's 25: computed by the original
# extractor and exported in its per-example TSV, but never analyzed.
EXTRA_SPEC = [
    ("n_questions", "Question count", "continuous", "Interactivity", "?"),
    ("n_discourse_markers", "Discourse marker count", "continuous", "Discourse Markers", "?"),
]

# Display format strings from the original FEATURE_SPEC, used by the report
# writers to reproduce the published table formatting.
FEATURE_FORMATS = {
    "has_question": "{:.1%}",
    "multi_question": "{:.1%}",
    "has_user_engage": "{:.1%}",
    "has_you_ref": "{:.1%}",
    "starts_with_ack": "{:.1%}",
    "has_exclamation": "{:.1%}",
    "has_opinion": "{:.1%}",
    "has_formulaic": "{:.1%}",
    "has_citation": "{:.1%}",
    "n_words": "{:.1f}",
    "n_sentences": "{:.1f}",
    "has_hedge": "{:.1%}",
    "n_hedges": "{:.2f}",
    "has_emphasizer": "{:.1%}",
    "n_emphasizers": "{:.2f}",
    "hedge_ratio": "{:.3f}",
    "has_discourse_marker": "{:.1%}",
    "self_ratio": "{:.3f}",
    "n_first_person": "{:.2f}",
    "n_second_person": "{:.2f}",
    "content_ratio": "{:.3f}",
    "ttr": "{:.3f}",
    "pm_density": "{:.4f}",
    "interactivity": "{:.3f}",
    "question_density": "{:.3f}",
}


def _register_all():
    for feature_id, name, kind, group, predicted in IVA2026_SPEC + EXTRA_SPEC:
        registry.register(Feature(
            id=feature_id,
            name=name,
            group=group,
            kind=kind,
            predicted=predicted,
            tags=frozenset(),
            fn=getattr(features, feature_id),
        ))
    registry.register_profile(Profile(
        name="iva2026",
        features=tuple(registry.get(spec[0]) for spec in IVA2026_SPEC),
        lexicon="iva2026",
        lexicon_version=1,
    ))


_register_all()

"""
Created by davan (with Claude assistance)
7/23/26

Loader for the frozen lexicon files shipped with lexfeat.

The iva2026 v1 lexicon is frozen: it carries the exact cue lists and regex
pattern that produced the published IVA 2026 numbers. Fixes and improvements
land in successor lexicon versions, never here. The extractor behavior the
published numbers embed includes eight deliberate quirks, each locked by a
unit test:

  1. Substring, not token, matching throughout — "about" inside
     "roundabout" counts as a hedge.
  2. ACK_STARTS and DISCOURSE_MARKERS_INITIAL match as prefixes only
     (the discourse-marker check runs on the first 50 characters of the
     lowercased text). "i mean" appears in both DISCOURSE_MARKERS_INITIAL
     and DISCOURSE_MARKERS_ANY, so it counts twice in n_discourse_markers
     when utterance-initial.
  3. Pronoun counts use space-padded substring counting, so trailing
     punctuation blocks a match ("you." is not counted as "you").
  4. SO_INTENSIFIER_RE has a closed adjective list; "so" + an adjective
     outside the list is not an emphasizer.
  5. hedge_ratio and self_ratio are None when their denominators are zero;
     analysis excludes the Nones from means (conditional features).
  6. Sentence count is the number of [.!?]+ regex segments, which includes
     one empty trailing segment when the text ends with punctuation
     ("Hi. Bye." has 3 segments).
  7. multi_question is derived as n_questions > 1.
  8. interactivity is the mean of exactly five binary features:
     has_question, has_user_engage, has_you_ref, starts_with_ack,
     has_exclamation.
"""

import json
from importlib import resources


def load_lexicon(name: str = "iva2026", version: int = 1) -> dict:
    """Load a lexicon shipped with the package; returns the parsed dict.

    The dict has keys: lexicon, version, frozen, provenance, lists (name ->
    list of cue strings), patterns (name -> regex pattern string).
    """
    fname = f"{name}.v{version}.json"
    with resources.files(__package__).joinpath(fname).open(encoding="utf-8") as fin:
        return json.load(fin)

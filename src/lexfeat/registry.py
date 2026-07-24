"""
Created by davan (with Claude assistance)
7/23/26

Feature dataclass, Registry, and Profile — the lexfeat core types.

The registry is flat: a feature's group is metadata, and profiles are free
to regroup. A Profile is a named, ordered feature selection pinned to a
lexicon version; Profile.extract(text) returns exactly the profile's keys.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Feature:
    id: str            # "has_question"
    name: str          # "Has question" (paper Table 5 label)
    group: str         # "Interactivity" — metadata only
    kind: str          # "binary" | "continuous" | "composite"
    predicted: str     # "A > B" | "B > A" | "A < B" | "n.s." | "?"
    tags: frozenset    # e.g. {"spoken", "stt"}; empty for v0.1 features
    fn: Callable       # (text, ctx) -> value


@dataclass(frozen=True)
class Profile:
    """Named, ordered feature selection pinned to a lexicon version."""

    name: str
    features: tuple    # ordered tuple of Feature
    lexicon: str
    lexicon_version: int

    def extract(self, text: str) -> dict:
        """Extract this profile's features from text; returns {id: value}.

        Operates on the text as given. SSML stripping is the caller's job
        (lexfeat.features.clean_text), matching the original pipeline where
        candidate text is cleaned before features are computed.
        """
        ctx = {}
        return {f.id: f.fn(text, ctx) for f in self.features}


class Registry:
    """Flat registry of features and profiles."""

    def __init__(self):
        self._features = {}
        self._profiles = {}

    def register(self, feature: Feature) -> None:
        if feature.id in self._features:
            raise ValueError(f"duplicate feature id: {feature.id}")
        self._features[feature.id] = feature

    def get(self, feature_id: str) -> Feature:
        return self._features[feature_id]

    def register_profile(self, prof: "Profile") -> None:
        if prof.name in self._profiles:
            raise ValueError(f"duplicate profile name: {prof.name}")
        self._profiles[prof.name] = prof

    def profile(self, name: str) -> "Profile":
        return self._profiles[name]


# Default registry; lexfeat.profiles populates it at import.
_DEFAULT = Registry()


def register(feature: Feature) -> None:
    _DEFAULT.register(feature)


def get(feature_id: str) -> Feature:
    return _DEFAULT.get(feature_id)


def register_profile(prof: Profile) -> None:
    _DEFAULT.register_profile(prof)


def profile(name: str) -> Profile:
    return _DEFAULT.profile(name)

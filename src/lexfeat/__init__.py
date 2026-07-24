"""
Created by davan (with Claude assistance)
7/23/26

lexfeat: lexical feature extraction and analysis of conversational style in
dialogue system responses. Companion artifact to Harrison & Walker (IVA 2026).
"""

from lexfeat import profiles as _profiles  # noqa: F401 — registers iva2026
from lexfeat.features import clean_text  # noqa: F401
from lexfeat.registry import Feature, Profile, Registry  # noqa: F401

__version__ = "0.1.0"

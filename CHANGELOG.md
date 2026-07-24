# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-24

### Added

- The frozen `iva2026` profile: the 25 linguistic features of Harrison &
  Walker (IVA 2026), with the exact published cue lists
  (`lexicons/iva2026.v1.json`) and extractor behavior, quirks documented
  and lock-tested.
- Feature registry (`Feature`, `Registry`, `Profile`) with
  `Profile.extract`, plus the raw-count registry features `n_questions`
  and `n_discourse_markers`.
- The paper's hand-rolled statistics as the public `stats` module
  (Kruskal-Wallis, Mann-Whitney U, chi-square 2xk/2x2, effect sizes,
  Bonferroni), scipy-cross-validated in tests.
- `analysis.rates_by_label` and `report` writers reproducing the paper's
  analysis pipeline and output formats byte-for-byte (LaTeX tables, JSON
  summary, figures, per-example TSV with the topic-column fix, D-4).
- A/B contrast tooling (`contrast`): 10 prioritized contrast types, key
  differences, pair-quality filters.
- Athena corpus loader and the paper's Table 3 RG filter
  (`corpus.filter_rgs`, `EXCLUDED_RGS_TABLE3`) — maintainer-facing.
- `lexfeat` CLI (`extract`, `analyze`, `contrast`) behind the `[cli]` extra.
- Published paper examples (`examples/paper_examples.jsonl`), a seeded
  synthetic demo corpus with generator, three runnable recipes, the
  numbers-only published reference summary with provenance, and the
  maintainer acceptance tool (`tools/verify_published_numbers.py`).

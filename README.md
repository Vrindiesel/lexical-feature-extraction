# lexical-feature-extraction

[![CI](https://github.com/Vrindiesel/lexical-feature-extraction/actions/workflows/ci.yml/badge.svg)](https://github.com/Vrindiesel/lexical-feature-extraction/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python ≥3.9](https://img.shields.io/badge/python-%E2%89%A53.9-blue.svg)](pyproject.toml)

Lexical and pragmatic feature extraction for analyzing conversational style
in dialogue system responses: 25 features spanning interactivity,
acknowledgment, formulaicity, pragmatic force, discourse markers,
self/other orientation, and information density, with the statistical
analysis pipeline that contrasts response quality classes. This is the
companion artifact to Harrison & Walker, *"Conversational Style in Open
Domain Dialogue Systems: What Makes a Response Sound Natural"* (IVA 2026) —
the exact lexicons, extractor, and statistics that produced the paper's
Tables 4–6.

## Install

```bash
pip install git+https://github.com/Vrindiesel/lexical-feature-extraction
```

The base install has **zero runtime dependencies** (pure stdlib). Extras:

| Extra    | Installs     | Enables                                    |
|----------|--------------|--------------------------------------------|
| `[cli]`  | typer        | the `lexfeat` console command              |
| `[viz]`  | matplotlib   | figure writers (tables/JSON work without)  |
| `[test]` | pytest, scipy, ruff | the test suite and scipy cross-checks |

```bash
pip install "lexical-feature-extraction[cli,viz] @ git+https://github.com/Vrindiesel/lexical-feature-extraction"
```

## Quickstart

```python
from lexfeat import registry, analysis, report

prof = registry.profile("iva2026")
feats = prof.extract("Oh nice! Do you have a dog?")
# feats["has_question"]    -> True
# feats["starts_with_ack"] -> True
# feats["has_user_engage"] -> True
# feats["n_words"]         -> 7
# feats["interactivity"]   -> 1.0

records = [{"text": "...", "label": "A"}, {"text": "...", "label": "B"}]  # your data
res = analysis.rates_by_label(records, prof, label_key="label",
                              pairwise=("A", "B"), correction="bonferroni")
report.write_feature_rates_tex(res, "feature_rates_table.tex")
report.write_feature_summary_json(res, "feature_summary.json")
```

## The feature set

The `iva2026` profile is the paper's Table 5: 25 features in publication
order. Binary features report rates; continuous and composite features
report means.

| id | Feature | Group | Kind | Predicted A–B |
|----|---------|-------|------|---------------|
| `has_question` | Has question | Interactivity | binary | A > B |
| `multi_question` | Multi-question | Interactivity | binary | A > B |
| `has_user_engage` | User engagement | Interactivity | binary | A > B |
| `has_you_ref` | You/your ref | Interactivity | binary | A > B |
| `starts_with_ack` | Starts w/ ack | Acknowledgement | binary | A > B |
| `has_exclamation` | Exclamation | Expressiveness | binary | A > B |
| `has_opinion` | Opinion marker | Expressiveness | binary | B > A |
| `has_formulaic` | Formulaic opening | Formulaicity | binary | B > A |
| `has_citation` | Citation pattern | Formulaicity | binary | n.s. |
| `n_words` | Word count | Structural | continuous | A < B |
| `n_sentences` | Sentence count | Structural | continuous | n.s. |
| `has_hedge` | Hedge presence | Pragmatic Force | binary | A > B |
| `n_hedges` | Hedge count | Pragmatic Force | continuous | A > B |
| `has_emphasizer` | Emphasizer presence | Pragmatic Force | binary | A > B |
| `n_emphasizers` | Emphasizer count | Pragmatic Force | continuous | A > B |
| `hedge_ratio` | Hedge-to-emph ratio | Pragmatic Force | continuous | ? |
| `has_discourse_marker` | Discourse marker | Discourse Markers | binary | A > B |
| `self_ratio` | Self-orientation | Self/Other | continuous | B > A |
| `n_first_person` | 1st person count | Self/Other | continuous | B > A |
| `n_second_person` | 2nd person count | Self/Other | continuous | A > B |
| `content_ratio` | Content word ratio | Info Density | continuous | A < B |
| `ttr` | Type-token ratio | Info Density | continuous | ? |
| `pm_density` | Pragmatic marker dens. | Composite | composite | A > B |
| `interactivity` | Interactivity index | Composite | composite | A > B |
| `question_density` | Question density | Composite | composite | A > B |

The registry also exposes `n_questions` and `n_discourse_markers` — raw
counts the original extractor computed and exported, outside the 25
analyzed features.

## Profiles and freezing

`iva2026` is **frozen**: its cue lists
([`src/lexfeat/lexicons/iva2026.v1.json`](src/lexfeat/lexicons/iva2026.v1.json))
and its extraction behavior reproduce the code that produced the published
numbers, quirks included — substring (not token) matching, prefix-only
acknowledgment/discourse-marker checks, space-padded pronoun counting, a
closed "so + adjective" intensifier list, `[.!?]+` sentence segmentation,
and None for conditional ratios with no markers. The eight quirks are
documented in the lexicon module docstring and each is locked by a unit
test. Improvements land in successor profiles; `iva2026` never mutates.

## Relationship to the published paper

The port is verified against the original analysis: the maintainer
acceptance run reproduces every value of the paper's feature summary
exactly (see below). Four documented deviations:

- **D-1.** Paper Tables 4/6 were computed on the *unfiltered* corpus
  (D = 22,099), while Tables 1/3 describe the filtered 35,623 set. The A/B
  columns and all A-vs-B tests are unaffected. The filter ships as
  `corpus.filter_rgs` with `EXCLUDED_RGS_TABLE3`.
- **D-2.** The interactivity index as implemented is the mean of five
  specific binary features (has_question, has_user_engage, has_you_ref,
  starts_with_ack, has_exclamation); the paper's "mean of Group 1 binary
  features" description is imprecise. The published values (A = .414,
  B = .312) come from the implemented definition, which this library keeps.
- **D-3.** The paper's A/B pair-extraction script ran with slightly drifted
  cue lists (missing "kinda", "kinda like"). The canonical `iva2026` lists
  are the analysis script's; the drift affected no published number.
- **D-4.** A per-example TSV metadata bug (empty topic column) is fixed in
  this port; it affected no analysis value.

**Data statement.** The underlying corpus — annotated response candidates
from live Alexa Prize SocialBot conversations — contains real user
utterances and is private; it does not ship here and never will. What ships
instead: the paper's published example texts
([`examples/paper_examples.jsonl`](examples/paper_examples.jsonl), transcribed
from the camera-ready with provenance), a seeded synthetic corpus for the
demos, and the numbers-only reference summary
([`reference/feature_summary.iva2026.json`](reference/feature_summary.iva2026.json)).

**Reproducibility map.**

| Paper artifact | In this repo | Runtime |
|----------------|--------------|---------|
| Tables 4 & 6 (all values) | [`tools/verify_published_numbers.py`](tools/verify_published_numbers.py) — maintainer-only (needs the private corpus); diffs every value against the shipped reference, exact equality | ~3 s |
| Table 4/6 spot values | `tests/test_reference.py` (T5) — no corpus needed | <1 s |
| Table 5 (feature inventory) | the `iva2026` profile + `report.write_feature_definitions_tex` | <1 s |
| Figure 3 pair types | [`examples/recipes/contrast_demo.py`](examples/recipes/contrast_demo.py) on the published pairs | <1 s |
| Analysis pipeline end to end | [`examples/recipes/analysis_demo.py`](examples/recipes/analysis_demo.py) on the synthetic corpus (seed logged in [`examples/synthetic/generate.py`](examples/synthetic/generate.py)) | ~5 s |

## Demos

All three run on committed data only:

```bash
python examples/recipes/extract_demo.py    # features of the paper's examples
python examples/recipes/analysis_demo.py   # full pipeline, synthetic corpus
python examples/recipes/contrast_demo.py   # Figure 3 A/B pair classification
```

`analysis_demo.py` output (excerpt) — the synthetic corpus reproduces the
paper's A/B direction on every injected dimension:

```
feature                      A       B      A-B  sig
has_question             0.900   0.000   +0.900  ***
starts_with_ack          0.420   0.000   +0.420  ***
has_opinion              0.000   0.500   -0.500  ***
has_formulaic            0.000   0.600   -0.600  ***
has_hedge                0.170   0.610   -0.440  ***
interactivity            0.694   0.000   +0.694  ***
```

## CLI

With the `[cli]` extra installed:

```bash
lexfeat extract --text "Oh nice! Do you have a dog?"
lexfeat analyze --in corpus.jsonl --label-key label --out results/
lexfeat contrast --in pairs.jsonl --out contrasts.jsonl
```

## Roadmap

- **v0.2** — the PERSONAGE-era `personage` profile (30 pragmatic markers +
  aggregation operations, `[personage]` extra), parse-based aggregation
  detectors (`[parsing]` extra), entropy metrics, and correlation recipes.

## Citation

If you use this library, please cite the paper (see also
[`CITATION.cff`](CITATION.cff)):

```bibtex
@inproceedings{harrison2026conversational,
  title     = {Conversational Style in Open Domain Dialogue Systems:
               What Makes a Response Sound Natural},
  author    = {Harrison, Vrindavan and Walker, Marilyn},
  booktitle = {ACM International Conference on Intelligent Virtual
               Agents (IVA 2026)},
  year      = {2026},
  month     = sep,
  address   = {Puebla, Mexico},
  publisher = {ACM},
  isbn      = {979-8-4007-2647-7},
  doi       = {10.1145/3806774.3827985}
}
```

## License

[Apache-2.0](LICENSE). See [`CHANGELOG.md`](CHANGELOG.md) for release
history.

Parts of this codebase were developed with Claude Code assistance.

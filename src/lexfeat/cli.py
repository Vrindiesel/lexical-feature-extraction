"""
Created by davan (with Claude assistance)
7/23/26

Typer CLI for lexfeat ([cli] extra): extract, analyze, contrast.

Each command is one call into the library. The console script entry point
(main) degrades with an install hint when typer is not installed.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

try:
    import typer
except ImportError:
    typer = None


def main():
    """Console entry point for the lexfeat command."""
    if typer is None:
        sys.stderr.write(
            "The lexfeat CLI requires the [cli] extra: "
            "pip install 'lexical-feature-extraction[cli]'\n")
        raise SystemExit(1)
    app()


def _read_jsonl(path):
    with open(path) as fin:
        return [json.loads(line) for line in fin if line.strip()]


if typer is not None:
    app = typer.Typer(help="Lexical feature extraction and analysis (IVA 2026).",
                      no_args_is_help=True)

    @app.command()
    def extract(
        profile: str = typer.Option("iva2026", help="Registry profile name."),
        text: Optional[str] = typer.Option(None, help="Extract from one string."),
        in_file: Optional[str] = typer.Option(
            None, "--in", help="JSONL file of records with a 'text' field."),
        out: Optional[str] = typer.Option(
            None, help="Output JSONL path (default: stdout)."),
    ):
        """Extract profile features from a string or a JSONL file."""
        from lexfeat import registry
        from lexfeat.features import clean_text

        prof = registry.profile(profile)
        if (text is None) == (in_file is None):
            raise typer.BadParameter("provide exactly one of --text or --in")
        if text is not None:
            rows = [{"text": text, "features": prof.extract(clean_text(text))}]
        else:
            rows = [{"text": r.get("text", ""),
                     "features": prof.extract(clean_text(r.get("text", "")))}
                    for r in _read_jsonl(in_file)]
        lines = "\n".join(json.dumps(r) for r in rows) + "\n"
        if out:
            with open(out, "w") as fout:
                fout.write(lines)
        else:
            sys.stdout.write(lines)

    @app.command()
    def analyze(
        in_file: str = typer.Option(..., "--in", help="JSONL corpus of records."),
        out: str = typer.Option(..., help="Output directory."),
        profile: str = typer.Option("iva2026", help="Registry profile name."),
        label_key: str = typer.Option("label", help="Record key holding the label."),
    ):
        """Run the rates-by-label analysis and write tables, summary, figures."""
        from lexfeat import analysis, registry, report

        prof = registry.profile(profile)
        res = analysis.rates_by_label(_read_jsonl(in_file), prof, label_key=label_key)
        os.makedirs(out, exist_ok=True)
        report.write_feature_definitions_tex(
            res, os.path.join(out, "feature_definitions_table.tex"))
        report.write_feature_rates_tex(
            res, os.path.join(out, "feature_rates_table.tex"))
        report.write_significance_tex(
            res, os.path.join(out, "significance_tests_table.tex"))
        report.write_feature_summary_json(
            res, os.path.join(out, "feature_summary.json"))
        report.write_figures(res, out)
        print(f"Analysis outputs written to {out}")

    @app.command()
    def contrast(
        in_file: str = typer.Option(
            ..., "--in", help="JSONL of pairs with 'a_text' and 'b_text'."),
        out: Optional[str] = typer.Option(
            None, help="Output JSONL path (default: stdout)."),
        profile: str = typer.Option("iva2026", help="Registry profile name."),
    ):
        """Classify A/B response pairs into contrast types."""
        from lexfeat import registry
        from lexfeat.contrast import classify_pair

        prof = registry.profile(profile)
        rows = [classify_pair(p.get("a_text", ""), p.get("b_text", ""), prof)
                for p in _read_jsonl(in_file)]
        lines = "\n".join(json.dumps(r) for r in rows) + "\n"
        if out:
            with open(out, "w") as fout:
                fout.write(lines)
        else:
            sys.stdout.write(lines)

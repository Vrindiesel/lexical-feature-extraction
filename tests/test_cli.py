"""
Created by davan (with Claude assistance)
7/23/26

CLI smoke tests via typer's runner; skipped cleanly when the [cli] extra
is not installed. All texts are hand-written synthetic strings.
"""

import json

import pytest

typer = pytest.importorskip("typer")

from typer.testing import CliRunner

from lexfeat.cli import app

runner = CliRunner()


def test_extract_text():
    result = runner.invoke(app, ["extract", "--text", "Oh nice! Do you like it?"])
    assert result.exit_code == 0
    row = json.loads(result.stdout)
    assert row["features"]["has_question"] is True
    assert row["features"]["starts_with_ack"] is True


def test_extract_requires_one_input():
    result = runner.invoke(app, ["extract"])
    assert result.exit_code != 0


def test_analyze_writes_outputs(tmp_path):
    corpus = tmp_path / "records.jsonl"
    rows = []
    for i in range(8):
        rows.append({"label": "A", "text": f"Oh nice! Do you enjoy topic {i}?"})
        rows.append({"label": "B", "text": f"Here's something I read about topic {i}."})
        rows.append({"label": "C", "text": f"Topic {i} is a topic."})
        rows.append({"label": "D", "text": "T"})
    corpus.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    out_dir = tmp_path / "out"
    result = runner.invoke(app, ["analyze", "--in", str(corpus), "--out", str(out_dir)])
    assert result.exit_code == 0, result.output
    summary = json.loads((out_dir / "feature_summary.json").read_text())
    assert len(summary) == 25
    assert (out_dir / "feature_rates_table.tex").exists()
    assert (out_dir / "significance_tests_table.tex").exists()
    assert (out_dir / "feature_definitions_table.tex").exists()


def test_contrast_pairs(tmp_path):
    pairs = tmp_path / "pairs.jsonl"
    pairs.write_text(json.dumps({
        "a_text": "Oh, do you like hiking?",
        "b_text": "Hiking is walking outdoors.",
    }) + "\n")
    result = runner.invoke(app, ["contrast", "--in", str(pairs)])
    assert result.exit_code == 0
    row = json.loads(result.stdout.splitlines()[-1])
    assert row["contrast_type"] == "ack_question_vs_info"
    assert row["priority"] == 2

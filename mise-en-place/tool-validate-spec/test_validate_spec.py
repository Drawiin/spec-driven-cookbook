"""Tests for validate_spec.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

CANONICAL_SECTIONS = [
    "## Problem",
    "## Who It's For",
    "## Constraints",
    "## Success Criteria",
    "## Out of Scope",
]


def _spec_body(include_sections=None):
    sections = include_sections if include_sections is not None else CANONICAL_SECTIONS
    lines = ["---", "status: approved", "version: 1", "date: 2026-05-22", "---", ""]
    for header in sections:
        lines.append(header)
        lines.append("Placeholder content.")
        lines.append("")
    return "\n".join(lines)


def test_approved_spec_exits_zero(tmp_path, monkeypatch):
    """Approved SPEC.md with all sections exits 0."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "SPEC.md").write_text(_spec_body(), encoding="utf-8")

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_draft_spec_exits_one(tmp_path, monkeypatch, capsys):
    """Draft status exits 1 with actionable stderr."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    content = _spec_body().replace("status: approved", "status: draft")
    (planning / "SPEC.md").write_text(content, encoding="utf-8")

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    assert "must be 'approved'" in capsys.readouterr().err


def test_missing_spec_exits_one(tmp_path, monkeypatch, capsys):
    """Missing SPEC.md exits 1 with not found message."""
    monkeypatch.chdir(tmp_path)

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    assert "not found" in capsys.readouterr().err


def test_malformed_frontmatter_exits_one(tmp_path, monkeypatch, capsys):
    """SPEC.md without YAML front-matter exits 1."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "SPEC.md").write_text(
        "# Spec\n\nNo front-matter block here.\n",
        encoding="utf-8",
    )

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    assert "no valid YAML front-matter" in capsys.readouterr().err


def test_approved_spec_has_required_sections(tmp_path, monkeypatch):
    """Approved SPEC.md with canonical section headers exits 0."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "SPEC.md").write_text(_spec_body(), encoding="utf-8")

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_approved_spec_missing_section_exits_one(tmp_path, monkeypatch, capsys):
    """Approved SPEC.md missing ## Constraints exits 1."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    sections = [s for s in CANONICAL_SECTIONS if s != "## Constraints"]
    (planning / "SPEC.md").write_text(_spec_body(include_sections=sections), encoding="utf-8")

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "missing required section" in err
    assert "## Constraints" in err

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


def _brownfield_spec_body(
    include_brownfield=True,
    project_type="brownfield",
    already_built_bullets=None,
    to_build_bullets=None,
    include_sections=None,
    omit_project_type=False,
):
    """Build SPEC.md body with optional brownfield sections."""
    sections = include_sections if include_sections is not None else CANONICAL_SECTIONS
    lines = ["---", "status: approved", "version: 1", "date: 2026-05-22"]
    if not omit_project_type and project_type:
        lines.append(f"project_type: {project_type}")
    lines.extend(["---", ""])
    if include_brownfield:
        built = already_built_bullets or ["- Existing auth flow"]
        to_build = to_build_bullets or ["- Add OAuth provider"]
        lines.append("## Already Built")
        lines.extend(built)
        lines.append("")
        lines.append("## To Build")
        lines.extend(to_build)
        lines.append("")
    for header in sections:
        lines.append(header)
        lines.append("Placeholder content.")
        lines.append("")
    return "\n".join(lines)


def test_brownfield_missing_already_built(tmp_path, monkeypatch, capsys):
    """Brownfield approved spec missing ## Already Built → exit 1."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    body = _brownfield_spec_body()
    body = body.replace("## Already Built\n- Existing auth flow\n\n", "")
    (planning / "SPEC.md").write_text(body, encoding="utf-8")

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    assert "Already Built" in capsys.readouterr().err


def test_brownfield_missing_to_build(tmp_path, monkeypatch, capsys):
    """Brownfield approved spec missing ## To Build → exit 1."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    body = _brownfield_spec_body()
    body = body.replace("## To Build\n- Add OAuth provider\n\n", "")
    (planning / "SPEC.md").write_text(body, encoding="utf-8")

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    assert "To Build" in capsys.readouterr().err


def test_brownfield_approved_passes(tmp_path, monkeypatch):
    """Brownfield with all sections and distinct bullets → exit 0."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "SPEC.md").write_text(_brownfield_spec_body(), encoding="utf-8")

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_brownfield_sections_without_project_type_fails(tmp_path, monkeypatch, capsys):
    """Brownfield sections without project_type → exit 1."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "SPEC.md").write_text(
        _brownfield_spec_body(omit_project_type=True),
        encoding="utf-8",
    )

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "brownfield" in err.lower() or "project_type" in err


def test_brownfield_missing_problem_section(tmp_path, monkeypatch, capsys):
    """Brownfield missing ## Problem → exit 1."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    sections = [s for s in CANONICAL_SECTIONS if s != "## Problem"]
    (planning / "SPEC.md").write_text(
        _brownfield_spec_body(include_sections=sections),
        encoding="utf-8",
    )

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    assert "Problem" in capsys.readouterr().err


def test_brownfield_duplicate_bullet_in_both_sections_fails(tmp_path, monkeypatch, capsys):
    """Identical bullet in Already Built and To Build → exit 1."""
    monkeypatch.chdir(tmp_path)
    planning = tmp_path / ".planning"
    planning.mkdir()
    dup = "- Same feature listed twice"
    (planning / "SPEC.md").write_text(
        _brownfield_spec_body(
            already_built_bullets=[dup],
            to_build_bullets=[dup],
        ),
        encoding="utf-8",
    )

    from validate_spec import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    assert "duplicate" in capsys.readouterr().err.lower()


def test_greenfield_regression_still_passes(tmp_path, monkeypatch):
    """Greenfield approved spec without brownfield sections still exits 0."""
    test_approved_spec_exits_zero(tmp_path, monkeypatch)

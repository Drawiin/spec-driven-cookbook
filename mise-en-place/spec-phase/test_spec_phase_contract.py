"""Contract tests for spec-phase/SKILL.md workflow structure."""
from pathlib import Path

SKILL = Path(__file__).parent / "SKILL.md"
CANONICAL_MAP_FILES = [
    "STACK.md",
    "ARCHITECTURE.md",
    "CONVENTIONS.md",
    "STRUCTURE.md",
    "TESTING.md",
    "INTEGRATIONS.md",
    "CONCERNS.md",
]


def _body_lines():
    lines = []
    for line in SKILL.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("#"):
            continue
        lines.append(line)
    return "\n".join(lines)


def test_step_1_4_after_scaffold_before_qa():
    text = SKILL.read_text(encoding="utf-8")
    assert text.find("## Step 1:") < text.find("Step 1.4") < text.find("## Step 2:")


def test_no_step_0_language():
    for line in SKILL.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert "Step 0" not in line


def test_all_seven_map_filenames_preloaded():
    text = SKILL.read_text(encoding="utf-8")
    for name in CANONICAL_MAP_FILES:
        assert name in text


def test_detect_brownfield_invocation_documented():
    text = SKILL.read_text(encoding="utf-8")
    assert "tool-detect-brownfield" in text or "detect_brownfield.py" in text


def test_invalid_json_stops_workflow():
    assert "invalid JSON" in SKILL.read_text(encoding="utf-8")


def test_continue_branch_documented():
    assert "Continue" in SKILL.read_text(encoding="utf-8")


def test_completeness_gate_documented():
    text = SKILL.read_text(encoding="utf-8")
    assert "has_codebase_map" in text
    assert "20 lines" in text or ">20 lines" in text


def test_brownfield_sections_in_assembly():
    text = SKILL.read_text(encoding="utf-8")
    assert "## Already Built" in text
    assert "## To Build" in text

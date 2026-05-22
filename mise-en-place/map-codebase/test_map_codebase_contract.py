"""Contract tests for map-codebase/SKILL.md workflow structure."""
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


def test_all_seven_filenames_documented():
    text = SKILL.read_text(encoding="utf-8")
    for name in CANONICAL_MAP_FILES:
        assert name in text


def test_scan_map_secrets_invocation():
    assert "scan_map_secrets" in SKILL.read_text(encoding="utf-8")


def test_completeness_gate_documented():
    text = SKILL.read_text(encoding="utf-8")
    assert "20 lines" in text or ">20 lines" in text


def test_parallel_mapper_focuses():
    assert "generalPurpose" in SKILL.read_text(encoding="utf-8")

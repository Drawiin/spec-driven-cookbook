---
type: community
cohesion: 0.09
members: 31
---

# Spec Validation Tests

**Cohesion:** 0.09 - loosely connected
**Members:** 31 nodes

## Members
- [[Approved SPEC.md missing  Constraints exits 1.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Approved SPEC.md with all sections exits 0.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Approved SPEC.md with canonical section headers exits 0.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Brownfield approved spec missing  Already Built → exit 1.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Brownfield approved spec missing  To Build → exit 1.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Brownfield missing  Problem → exit 1.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Brownfield sections without project_type → exit 1.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Brownfield with all sections and distinct bullets → exit 0.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Build SPEC.md body with optional brownfield sections.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Draft status exits 1 with actionable stderr.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Greenfield approved spec without brownfield sections still exits 0.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Identical bullet in Already Built and To Build → exit 1.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Missing SPEC.md exits 1 with not found message.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[SPEC.md without YAML front-matter exits 1.]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[Tests for validate_spec.py]] - rationale - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[_brownfield_spec_body()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[_spec_body()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_approved_spec_exits_zero()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_approved_spec_has_required_sections()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_approved_spec_missing_section_exits_one()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_brownfield_approved_passes()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_brownfield_duplicate_bullet_in_both_sections_fails()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_brownfield_missing_already_built()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_brownfield_missing_problem_section()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_brownfield_missing_to_build()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_brownfield_sections_without_project_type_fails()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_draft_spec_exits_one()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_greenfield_regression_still_passes()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_malformed_frontmatter_exits_one()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_missing_spec_exits_one()]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py
- [[test_validate_spec.py]] - code - mise-en-place/tool-validate-spec/test_validate_spec.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Spec_Validation_Tests
SORT file.name ASC
```

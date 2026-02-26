# Backlog

Derived from session sweep of uncommitted changes and codebase state.
Context: repomix-output.xml (scripts/ directory snapshot, 2026-02-25).

## Summary

| Priority | Total | Done | Remaining |
|----------|-------|------|-----------|
| High     | 2     | 2    | 0         |
| Medium   | 2     | 2    | 0         |
| Low      | 1     | 1    | 0         |
| Review   | 8     | 2    | 6         |

---

## High Priority

### H1 — Commit scripts/shared/ utility module

**Status:** Done

Consolidates duplicated utilities from 13+ scripts into a single importable module:
- `clip_utils.py` — `CLIPClassifier` class (was duplicated in 4 scripts)
- `constants.py` — `IMAGE_EXTENSIONS`, `CLIP_CONTENT_LABELS`, `CONTENT_TO_SCHEMA`, game keywords, etc. (duplicated in 6+ scripts)
- `db_utils.py` — `get_db_connection`, `DEFAULT_DB_PATH` (duplicated in 4 scripts)
- `file_ops.py` — `resolve_collision` (duplicated in 5 scripts)
- `ocr_utils.py` — `extract_ocr_text`, `is_ocr_available` (duplicated in 3 scripts)
- `__init__.py` — re-exports for convenience

**Files:** `scripts/shared/__init__.py`, `scripts/shared/clip_utils.py`, `scripts/shared/constants.py`, `scripts/shared/db_utils.py`, `scripts/shared/file_ops.py`, `scripts/shared/ocr_utils.py`

---

### H2 — Commit 13 scripts refactored to use shared utilities

**Status:** Done

Removes 703 lines of duplicate code, adds 127 lines of imports (net: -576 lines).
All scripts now import from `shared.*` instead of defining inline.

**Files:** `scripts/add_content_descriptions.py`, `scripts/analyze_renamed_files.py`, `scripts/data_preprocessing.py`, `scripts/evaluate_model.py`, `scripts/generate_timeline_data.py`, `scripts/image_content_analyzer.py`, `scripts/image_content_renamer.py`, `scripts/merge_labeled_data.py`, `scripts/migrate_ids.py`, `scripts/organize_by_content.py`, `scripts/organize_to_existing.py`, `scripts/screenshot_renamer.py`, `scripts/update_report_with_labels.py`

---

## Medium Priority

### M1 — Commit staged cost_report.json update

**Status:** Done

`_site/cost_report.json` is already staged. Commit it as a separate data update.

**Files:** `_site/cost_report.json`

---

### M2 — Fix launch_timeline.sh broken path reference

**Status:** Done

`scripts/launch_timeline.sh` calls `python3 src/api/timeline_api.py` which does not exist.
The correct script is `scripts/generate_timeline_data.py`.

**File:** `scripts/launch_timeline.sh`

---

## Low Priority

### L1 — Add shared/ path note to CLAUDE.md

**Status:** Done

Document that `scripts/shared/` requires the caller's working directory to be the project root
(or `scripts/` added to `sys.path`) when running scripts directly. Add a note under
the Project Structure section in CLAUDE.md.

**File:** `CLAUDE.md`

---

---

## Review Findings (added from code review of H2)

### R1 — Fix organize_to_existing.py coverage gap (8 missing content types)

**Status:** Done

The hardcoded `if '_pet_' in fname_lower` elif chain handles only 12 of 20 content types.
Eight abbreviations from `CONTENT_ABBREVIATIONS` are unreachable:
`mobile`, `landscape`, `cityscape`, `vehicle`, `building`, `event`, `sports`, `abstract`.

Fix: replace the if/elif chain with a reverse lookup over `CONTENT_ABBREVIATIONS`.

**File:** `scripts/organize_to_existing.py`

---

### R2 — Use db_connection() context manager in generate_timeline_data.py

**Status:** Done

Five functions open connections with `get_db_connection()` + manual `conn.close()`.
If any raises before `conn.close()`, the connection leaks.
The `db_connection()` context manager added in H1 was designed for exactly this.

**File:** `scripts/generate_timeline_data.py`

---

### R3 — Fix Image.open() file handle leak in image_content_renamer.py

**Status:** Pending

The `_get_date_string` method (line 149) calls `Image.open(image_path).convert("RGB")` without a context manager.
On macOS with HEIC files, Pillow can hold file descriptors open, causing issues when processing large directories.

**File:** `scripts/image_content_renamer.py:149`

---

### R4 — Document _ABBREV_TO_CONTENT first-match priority in organize_to_existing.py

**Status:** Pending

A filename like `_screenshot_landscape_photo.jpg` matches both abbreviations. The loop takes the first match with `break`,
making the result dependent on `CONTENT_ABBREVIATIONS` insertion order. Add a comment explaining the priority guarantee.

**File:** `scripts/organize_to_existing.py:64–67`

---

### R5 — Update typing imports to modern syntax in analyze_renamed_files.py and image_content_renamer.py

**Status:** Pending

Both scripts import `from typing import Dict, List, Optional, Tuple` (old-style) instead of using Python 3.10+ union syntax
(`str | None` instead of `Optional[str]`). Session updated `ocr_utils.py` to modern syntax; these should match.

**Files:** `scripts/analyze_renamed_files.py:14`, `scripts/image_content_renamer.py:12`

---

### R6 — Fix Pillow context manager semantics in ocr_utils.py

**Status:** Pending

The `extract_ocr_text` function calls `img.convert('RGB')` inside a `with Image.open()` block. When `convert()` is called,
it returns a new `Image` object; the original context-managed image will close, but the converted copy is not context-managed.
Rename the raw image to clarify: `with Image.open() as raw_img: img = raw_img.convert() if ... else raw_img`.

**File:** `scripts/shared/ocr_utils.py:39–42`

---

### R7 — Add db_connection() auto-commit documentation

**Status:** Pending

The `db_connection()` context manager docstring should document that it does NOT auto-commit. Callers must call
`conn.commit()` explicitly after writes, or wrap the transaction with `with conn:`.

**File:** `scripts/shared/db_utils.py`

---

### R8 — Add unit tests for scripts/shared/ module

**Status:** Pending

The six files in `scripts/shared/` have no unit test coverage. Existing test fixtures in `tests/conftest.py`
(`temp_dir`, `temp_db_path`, `sample_image_file`) would make it trivial to test `resolve_collision`, `get_db_connection`,
`db_connection`, and `extract_ocr_text`. Priority: should be added before major refactoring of these utilities.

**Files:** `scripts/shared/*`, `tests/unit/test_shared.py` (new)

---

_Last updated: 2026-02-25_

# Backlog

Derived from session sweep of uncommitted changes and codebase state.
Context: repomix-output.xml (scripts/ directory snapshot, 2026-02-25).

## Open Items

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

_Last updated: 2026-03-28_ | _8 items migrated to docs/changelog/2.0.0/CHANGELOG.md_

# Backlog

Derived from session sweep of uncommitted changes and codebase state.
Context: repomix-output.xml (scripts/ directory snapshot, 2026-02-25).

## Open Items

### S1 — Unit tests for SchemaOrgExporter
**File to create:** `src/tests/test_schema_org_exporter.py`
**Source:** `REFACTORING_INDEX.md` Phase 3
Cover: `export_to_file`, `export_to_ndjson`, `export_with_graph`, and entity-filtered exports.
Use `tmp_path` fixture and a seeded in-memory session.

### S2 — Integration tests for schema_org_variants
**File to create:** `src/tests/test_schema_org_variants.py`
**Source:** `REFACTORING_INDEX.md` Phase 3
Cover: `CategoryVariants`, `PersonVariants`, `FileVariants` — all representations against real model instances.

### S3 — End-to-end export tests
**File to create:** `src/tests/test_schema_org_export_e2e.py`
**Source:** `REFACTORING_INDEX.md` Phase 3
Cover: full pipeline from DB population → export → JSON-LD structure validation for each output format.

### S5 — Document property mappings in code comments
**Files:** `src/storage/schema_org_builders.py`, model `to_schema_org()` methods
**Source:** `REFACTORING_GUIDE.md` § Next Steps
Add inline comments mapping each emitted property to its schema.org spec URL (e.g., `# https://schema.org/dateCreated`). Covers builder functions and all five model `to_schema_org()` implementations.

### S4 — Performance testing for export pipeline
**Source:** `REFACTORING_INDEX.md` Phase 4
Benchmark `SchemaOrgExporter` against representative data sizes (1k, 10k, 100k entities).
Establish baseline and add regression guard (e.g., pytest-benchmark).

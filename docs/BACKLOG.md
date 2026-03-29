# Backlog

Derived from session sweep of uncommitted changes and codebase state.
Context: repomix-output.xml (scripts/ directory snapshot, 2026-02-25).

## Open Items

### S1 — Unit tests for SchemaOrgExporter ✓ DONE
**File created:** `tests/unit/test_schema_org_exporter.py`
**Source:** `REFACTORING_INDEX.md` Phase 3
Covers: `export_to_file`, `export_to_ndjson`, `export_with_graph`, `get_graph_document`, entity-filtered exports.
Uses `tmp_path` fixture and a seeded in-memory session. 32 tests, all pass.
Also created: `src/storage/schema_org_exporter.py` (SchemaOrgExporter implementation).

### S2 — Integration tests for schema_org_variants ✓ DONE
**File created:** `tests/unit/test_schema_org_variants.py`
**Source:** `REFACTORING_INDEX.md` Phase 3
Covers: `CategoryVariants`, `PersonVariants`, `FileVariants` — all representations against real model instances.
28 tests, all pass.
Also created: `src/storage/schema_org_variants.py` (CategoryVariants, PersonVariants, FileVariants implementation).

### S3 — End-to-end export tests ✓ DONE
**File created:** `tests/integration/test_schema_org_export_e2e.py`
**Source:** `REFACTORING_INDEX.md` Phase 3
Covers: full pipeline from DB population → export → JSON-LD structure validation for all output formats (json, ndjson, @graph).
26 tests, all pass.

### S5 — Document property mappings in code comments
**Files:** `src/storage/schema_org_builders.py`, model `to_schema_org()` methods
**Source:** `REFACTORING_GUIDE.md` § Next Steps
Add inline comments mapping each emitted property to its schema.org spec URL (e.g., `# https://schema.org/dateCreated`). Covers builder functions and all five model `to_schema_org()` implementations.

### S4 — Performance testing for export pipeline
**Source:** `REFACTORING_INDEX.md` Phase 4
Benchmark `SchemaOrgExporter` against representative data sizes (1k, 10k, 100k entities).
Establish baseline and add regression guard (e.g., pytest-benchmark).

### S6 — Update REST API endpoints to use SchemaOrgExporter
**Source:** `RECOMMENDATIONS_APPLIED.md` Phase 4
**Files:** REST API endpoint handlers (locate via `grep -r "schema_org" src/`)
Update all REST API endpoints to serve JSON-LD output via `SchemaOrgExporter` rather than
ad-hoc serialization. Ensure `@context` and `@graph` structure is preserved in responses.

### S7 — JSON-LD validation against schema.org
**Source:** `REFACTORING_GUIDE.md` § Next Steps #4
**Files:** `src/tests/test_schema_org_serialization.py` or new `src/tests/test_schema_org_validation.py`
Current tests assert structural JSON-LD shape but do not validate against the schema.org vocabulary.
Integrate an external validator (e.g., `pyshacl` with the schema.org SHACL shapes, or `jsonschema` with a custom schema.org JSON Schema) to confirm emitted properties are recognized schema.org terms and values match expected types.
Cover at minimum: `File` (ImageObject/VideoObject), `Category` (DefinedTerm), `Company` (Organization), `Person`, `Location` (Place/City/Country).

### S8 — JSON-LD context file generation for complex graphs
**Source:** `REFACTORING_GUIDE.md` § Next Steps #6
**Files:** `src/storage/schema_org_exporter.py`, new `src/storage/schema_org_context.py`
Generate a standalone JSON-LD `@context` document that maps all custom and schema.org terms used in exports.
Required for consumers that resolve `@context` by URL rather than embedding it inline.
Cover: custom `ml:` namespace (`ml:hasFaces`), all schema.org properties emitted by the five entity models, and the `@graph` export format.
Expose via a `SchemaOrgExporter.export_context()` method and optionally a `/schema/context` API endpoint.

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
**Files:** model `to_schema_org()` methods in `src/storage/models.py`
Add inline comments mapping each emitted property to its schema.org spec URL (e.g., `# https://schema.org/dateCreated`). Covers builder functions and all five model `to_schema_org()` implementations.

### S4 — Performance testing for export pipeline ✓ DONE
**File created:** `tests/performance/test_export_benchmark.py`
**Source:** `REFACTORING_INDEX.md` Phase 4
Benchmarks all four `SchemaOrgExporter` methods (`get_graph_document`, `export_to_file`, `export_to_ndjson`, `export_with_graph`) at 100, 1k, and 10k entities (10k gated behind `@pytest.mark.slow`).
Baseline workflow: `pytest tests/performance/ --benchmark-save=baseline -m "not slow"` then `--benchmark-compare=baseline`.

### S6 — Update REST API endpoints to use SchemaOrgExporter ✓ DONE
**Source:** `RECOMMENDATIONS_APPLIED.md` Phase 4
**Files:** `src/api/schema_org_api.py`
Updated bulk export endpoint (`/api/schema-org/export`) to use `SchemaOrgExporter.get_graph_document()` and return a proper JSON-LD `@context`/`@graph` document.
Added `/api/schema-org/graph` endpoint for full graph export via `SchemaOrgExporter`.
Added `/schema/context` endpoint that returns the standalone JSON-LD context document.
Single-entity endpoints remain with direct `model.to_schema_org()`.

### S7 — JSON-LD validation against schema.org ✓ DONE
**File created:** `tests/unit/test_schema_org_validation.py`
44 tests, all pass. Uses `jsonschema` with custom schemas covering all five entity types.
Three test classes: `TestContextAndTypeValidation`, `TestRequiredProperties`, `TestPropertyValueTypes`.
Validates `@context`, `@type` (against known valid schema.org types), `@id` format, required fields per type, and property value types (strings, ints, booleans, nested objects).
Covers: File (ImageObject/VideoObject/DigitalDocument), Category (DefinedTerm), Company (Organization), Person, Location (Place/City/Country).

### S9 — Search endpoints: include schema.org context in responses
**Source:** `SCHEMA_ORG_ALIGNMENT.md` § Integration Points
**Files:** `src/api/schema_org_api.py` search/filter endpoints
Ensure any search or filter endpoints return responses wrapped with `@context` and valid JSON-LD structure, not bare JSON objects.

### S10 — Performance impact analysis for schema.org serialization
**Source:** `SCHEMA_ORG_ALIGNMENT.md` § Integration Points
**Files:** `tests/performance/test_export_benchmark.py`
Extend the existing benchmark suite to measure per-entity `to_schema_org()` serialization cost and relationship-building overhead. Establish baselines at 100/1k/10k entities.

### S8 — JSON-LD context file generation for complex graphs ✓ DONE
**File created:** `src/storage/schema_org_context.py`
**Modified:** `src/storage/schema_org_exporter.py`, `src/api/schema_org_api.py`
`schema_org_context.py` generates a standalone JSON-LD `@context` document with `@vocab`, `schema:` and `ml:` prefixes, and property mappings for all five entity models.
`SchemaOrgExporter.get_context_document()` returns the context as a dict; `SchemaOrgExporter.export_context(output_path)` saves to file.
`/schema/context` API endpoint added to `schema_org_api.py`.
Covers: `ml:hasFaces`, `ml:fileCount`, `ml:hierarchyLevel`, `ml:mentionCount`, `ml:geoHash`, and all schema.org properties emitted by File/Category/Company/Person/Location models.

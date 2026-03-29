# Changelog

All notable changes to the Schema.org File Organization System.

## [1.6.0] - 2026-03-28

### Added

- **SchemaOrgSerializable mixin** (`src/storage/schema_org_base.py`) — JSON-LD interface standardized across all models (`575d2d8`)
- **Unit tests for scripts/shared/** (`tests/unit/test_shared.py`) — 141 lines covering `resolve_collision`, `get_db_connection`, `db_connection`, `extract_ocr_text` (`a63eac7`)

### Refactored

- Wire `SchemaOrgSerializable` into all storage models; retire `REFACTORING_INDEX.md` (`95a98a9`)
- Replace EXIF magic numbers with named constants in `image_content_renamer.py` (`235fb18`)
- Update typing imports to modern syntax (`str | None` over `Optional[str]`) in `analyze_renamed_files.py` and `image_content_renamer.py` (`0eaad81`)

### Fixed

- Fix `Image.open()` file handle leak in `image_content_renamer.py` — use context manager in `_get_date_string` (`5c69a40`)
- Document `_ABBREV_TO_CONTENT` first-match priority in `organize_to_existing.py` (`dfe639c`)
- Add `db_connection()` auto-commit documentation to `scripts/shared/db_utils.py` (`4a12c93`)

---

## [1.5.0] - 2026-03-24

### Fixed

#### JSON-LD Compliance — Remove non-standard keys from exporter

Removed non-standard `generated` and `entityCount` fields from `export_with_graph()` output.
Exports now conform to the JSON-LD specification: `{"@context": "...", "@graph": [...]}` only.

**File:** `src/storage/schema_org_exporter.py`

---

#### Replace deprecated `datetime.utcnow()`

Removed the only usage of `datetime.utcnow()` (deprecated in Python 3.12+).
Added `timezone` to imports for future-safe datetime handling via `datetime.now(timezone.utc)`.

**File:** `src/storage/schema_org_exporter.py`

---

#### Country code truncation bug in `build_postal_address()`

`country[:2]` produced invalid ISO codes (e.g. `'France' → 'Fr'`).
Added `_COUNTRY_CODE_MAPPING` (30+ countries) and `_normalize_country_code()` with support for:
- 2-char ISO codes (`'US' → 'US'`)
- Full country names (`'France' → 'FR'`)
- Case-insensitive and prefix matching (`'fra' → 'FR'`)

**File:** `src/storage/schema_org_builders.py`

---

### Refactored

#### Remove duplicate `build_schema_reference()` definition

`build_schema_reference()` in `schema_org_base.py` was identical to `build_entity_reference()`
in `schema_org_builders.py`. Removed the duplicate; canonical definition lives in builders.

**Files:** `src/storage/schema_org_base.py`, `src/storage/schema_org_builders.py`

---

#### Namespace custom `hasFaces` property on `ImageObject`

`hasFaces` is not a standard schema.org property. Renamed to `ml:hasFaces` to indicate a
machine-learning custom extension. Requires a custom `@context` entry to resolve:

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "ml": "https://example.org/ml-properties/"
  }
}
```

**File:** `src/storage/schema_org_builders.py`

---

## [1.4.0] - 2026-02-01

### Added
- **Image Content Renamer** (`image_content_renamer.py`) - CLIP vision-based image renaming with categories
- **Image Content Analyzer** (`image_content_analyzer.py`) - Generate object IDs and descriptions
- **E2E Testing** - Playwright tests with OpenTelemetry instrumentation
  - `dashboard.spec.ts`, `timeline.spec.ts`, `metadata-viewer.spec.ts`, `correction-interface.spec.ts`
  - Fixtures: otel-tracing, performance, har-recording, traffic-tracking

### Classification Categories
- Legal/Contract detection (contracts, agreements, terms)
- E-commerce/Shopping detection (product listings, carts)
- Software UI detection (app interfaces, dashboards)
- Marketing/Infographic content
- Docs/Documentation
- CRM/HR/Meeting Notes business subcategories
- Source-based photo organization
- Game audio routing patterns

### Improved
- Person detection with OCR enhancement
- Game asset detection expanded to 200+ patterns including audio
- Screenshot renamer output recognition in content organizer
- Company name filtering and normalization

### Fixed
- Exclude data visualization terms from game asset classification
- Exclude 'command' key from argv passthrough in CLI
- Expand tilde in `--base-path` to prevent literal `~/` directory
- Prevent CSS files matching business patterns

### Metrics
- Files processed: 265,000+
- Source files: 61+
- Test modules: 20+

---

## [1.3.0] - 2025-12-10

### Added
- Entity-based folder organization (`Organization/`, `Person/`)
- Canonical IDs (UUID v5 + SHA256)
- Cost/ROI tracking with manual time savings calculation
- Sentry SDK v2 integration

### Classification Priority (v1.3)
1. Organization Detection
2. Person Detection
3. Game Asset Detection (200+ patterns)
4. Filepath Matching
5. Content Analysis (OCR + CLIP)
6. MIME Type Fallback

### Metrics
- Files processed: 72,978+
- Success rate: 98.6%
- Top category: GameAssets (84.8%)

---

## [1.2.0] - 2025-11-15

### Added
- Schema.org JSON-LD metadata generation
- GraphStore with SQLAlchemy ORM
- Web dashboard (_site/) with timeline visualization

---

## [1.1.0] - 2025-10-01

### Added
- CLIP vision model integration
- Tesseract OCR for text extraction
- Game asset detection patterns

---

## [1.0.0] - 2025-09-01

### Initial Release
- Basic file organization by type and name
- SQLite database storage
- CLI interface (`organize-files`)

# Changelog

All notable changes to the Schema.org File Organization System.

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

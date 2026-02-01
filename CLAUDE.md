# Schema.org File Organization System

AI-powered file organization using CLIP vision, OCR, Schema.org metadata, and entity detection.

## Quick Start

```bash
source venv/bin/activate
organize-files content --source ~/Downloads --dry-run --limit 100
organize-files health                    # Check dependencies
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `organize-files content` | AI-powered organization (CLIP, OCR) |
| `organize-files name` | Filename pattern organization (no AI) |
| `organize-files type` | Extension-based organization |
| `organize-files health` | Check system dependencies |
| `organize-files migrate-ids` | Run database migration |
| `organize-files update-site` | Update dashboard data |

## Project Structure

```
├── src/                    # Core library
│   ├── cli.py              # Unified CLI entry point
│   ├── generators.py       # Schema.org metadata generation
│   ├── error_tracking.py   # Sentry integration
│   └── storage/
│       └── graph_store.py  # SQLAlchemy graph with canonical IDs
├── scripts/
│   ├── file_organizer_content_based.py  # Main AI organizer
│   ├── image_content_renamer.py         # CLIP-based image renaming
│   └── image_content_analyzer.py        # Image content analysis
├── tests/
│   ├── unit/               # Unit tests (pytest)
│   └── e2e/                # E2E tests (Playwright + OpenTelemetry)
├── _site/                  # Dashboard UI
└── results/                # Reports & database
```

## Classification Priority

1. **Organization Detection** - client, vendor, invoice, company names
2. **Person Detection** - resume, contact, signatures (OCR-enhanced)
3. **Legal/Contract** - contracts, agreements, terms
4. **E-commerce/Shopping** - product listings, carts
5. **Software UI** - app interfaces, dashboards
6. **Game Assets** - 200+ patterns, sprites, textures, audio
7. **Filepath Matching** - directory structure patterns
8. **Content Analysis** - OCR text and CLIP vision
9. **MIME Type Fallback** - file extension

## Output Folders

```
~/Documents/
├── Organization/{CompanyName}/    # Vendor/partner files
├── Person/{PersonName}/           # Person-related files
├── GameAssets/                    # Sprites, textures, models
├── Financial/                     # Invoices, receipts
├── Technical/                     # Code, configs
└── Media/                         # Photos, videos, audio
```

## Environment

| Variable | Description |
|----------|-------------|
| `FILE_SYSTEM_SENTRY_DSN` | Sentry error tracking (Doppler) |
| `--sentry-dsn` | CLI override |

## Dependencies

```bash
pip install -e ".[all]" && brew install tesseract poppler
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| HEIC fails | `pip install pillow-heif` |
| No OCR | `brew install tesseract` |
| No AI | `pip install torch transformers` |

---
**Python:** 3.14 | **Version:** 1.4.0 | **Files:** 265,000+ processed

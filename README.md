# Schema.org File Organization System

AI-powered file organization using CLIP vision, OCR, Schema.org metadata, and entity detection.

**Version:** 1.4.0 | **Python:** 3.8 - 3.14 | **Files Processed:** 265,000+

## Quick Start

```bash
# Setup
git clone https://github.com/aledlie/schema-org-file-system.git
cd schema-org-file-system
python3 -m venv venv && source venv/bin/activate
pip install -e ".[all]"
brew install tesseract poppler

# Run
organize-files content --source ~/Downloads --dry-run --limit 100
organize-files health  # Check dependencies
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `organize-files content` | AI-powered organization (CLIP, OCR) |
| `organize-files name` | Filename pattern organization |
| `organize-files type` | Extension-based organization |
| `organize-files health` | Check system dependencies |
| `organize-files migrate-ids` | Run database migration |
| `organize-files update-site` | Update dashboard data |

## Architecture

```mermaid
flowchart LR
    A[Source Files] --> B[CLI]
    B --> C{Organizer}
    C --> D[CLIP Vision]
    C --> E[OCR]
    C --> F[Entity Detection]
    D & E & F --> G[Category Assignment]
    G --> H[GraphStore]
    H --> I[(SQLite)]
    H --> J[Schema.org JSON-LD]
    I & J --> K[Dashboard]
```

## Classification Priority

1. **Organization** - client, vendor, invoice, company names
2. **Person** - resume, contact, signatures (OCR-enhanced)
3. **Legal/Contract** - contracts, agreements, terms
4. **E-commerce** - product listings, shopping carts
5. **Software UI** - app interfaces, dashboards
6. **Game Assets** - 200+ patterns, sprites, textures, audio
7. **Filepath** - directory structure patterns
8. **Content Analysis** - OCR text + CLIP vision
9. **MIME Type** - file extension fallback

## Project Structure

```
├── src/                    # Core library
│   ├── cli.py              # CLI entry point
│   ├── generators.py       # Schema.org generators
│   └── storage/            # GraphStore, models
├── scripts/                # Organizer scripts
├── tests/                  # Unit, integration, e2e
├── _site/                  # Web dashboard
└── results/                # Database & reports
```

## Output Folders

```
~/Documents/
├── Organization/{Company}/    # Vendor/partner files
├── Person/{Name}/             # Person-related files
├── GameAssets/                # Sprites, textures, models
├── Financial/                 # Invoices, receipts
├── Technical/                 # Code, configs
└── Media/                     # Photos, videos, audio
```

## Key Features

- **Entity Detection** - Prioritizes Organization and Person identification
- **Canonical IDs** - UUID v5 + SHA256 for persistent identification
- **Schema.org Metadata** - Full JSON-LD generation
- **Cost Tracking** - ROI calculation with manual time savings
- **E2E Testing** - Playwright with OpenTelemetry instrumentation

## Tech Stack

| Layer | Technology |
|-------|------------|
| AI/ML | PyTorch, CLIP, OpenCV |
| OCR | Tesseract |
| Database | SQLite + SQLAlchemy |
| Monitoring | Sentry SDK |
| Testing | pytest, Playwright |

## Documentation

- [CHANGELOG](docs/CHANGELOG.md) - Version history
- [DEPENDENCIES](docs/DEPENDENCIES.md) - Installation guide
- [ARCHITECTURE_REFACTOR](docs/ARCHITECTURE_REFACTOR.md) - Design decisions

## Changelog

### v1.4.0 (Recent)

**Features**
- Typed subdirectories for screenshot categories
- Enhanced weak image classification with full CLIP + OCR fallback
- Shared utilities module consolidating 576 lines of duplication

**Fixes**
- Route profile.png → Portraits, REWORK.png → Data Visualization
- Route logo images → Organization/Integrity Studio
- Legal/contract detection before event pattern matching
- All 20 content types covered in organize_to_existing.py

**Docs**
- Visual architecture diagrams with mermaid flowcharts
- System overview, database schema, and module dependencies

**See full history:** `git log --oneline` | **Last commit:** 4b8f578 (2026-03-19)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `FILE_SYSTEM_SENTRY_DSN` | Sentry error tracking (Doppler) |
| `--sentry-dsn` | CLI override |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| HEIC fails | `pip install pillow-heif` |
| No OCR | `brew install tesseract` |
| No AI | `pip install torch transformers` |
| Check deps | `organize-files health` |

## Visual Architecture

### System Overview

```mermaid
flowchart TB
    subgraph Input
        U[User] --> CLI[organize-files CLI]
        F[Source Files] --> CLI
    end

    subgraph Processing["Processing Pipeline"]
        CLI --> CO{Organizer Type}
        CO -->|content| AI[AI Organizer]
        CO -->|name| NM[Name Organizer]
        CO -->|type| TY[Type Organizer]

        AI --> CLIP[CLIP Vision]
        AI --> OCR[Tesseract OCR]
        AI --> ED[Entity Detection]
        AI --> GAD[Game Asset Detection]
        AI --> LCD[Legal/Contract]
        AI --> ECD[E-commerce]
        AI --> SUI[Software UI]
    end

    subgraph Storage
        CLIP & OCR & ED & GAD & LCD & ECD & SUI --> GS[GraphStore]
        GS --> DB[(SQLite)]
        GS --> JSON[Schema.org JSON-LD]
    end

    subgraph Output
        DB --> DASH[Web Dashboard]
        JSON --> DASH
        DB --> RPT[Reports]
    end

    subgraph Monitoring
        AI -.-> SENTRY[Sentry]
        AI -.-> COST[Cost Tracker]
    end

    subgraph External
        CLIP -.-> HF[HuggingFace]
        ED -.-> NOM[Nominatim]
    end
```

### Database Schema

```mermaid
erDiagram
    File ||--o{ FileCategory : has
    File ||--o{ FileCompany : has
    File ||--o{ FilePerson : has
    File ||--o{ FileLocation : has
    File ||--o{ FileRelationship : source
    File ||--o{ FileRelationship : target
    File }o--|| OrganizationSession : belongs_to

    File {
        string id PK "SHA-256"
        string canonical_id "UUID v5"
        string filename
        string original_path
        string current_path
        enum status
        string schema_type
        string content_hash
    }

    Category {
        int id PK
        string canonical_id
        string name
        int parent_id FK
        string full_path
    }

    Company {
        int id PK
        string canonical_id
        string name
        string normalized_name
        string domain
    }

    Person {
        int id PK
        string canonical_id
        string name
        string email
        string role
    }

    Location {
        int id PK
        string canonical_id
        string city
        string state
        float lat
        float lng
    }

    OrganizationSession {
        uuid id PK
        datetime started_at
        int total_files
        float total_cost
    }

    CostRecord {
        int id PK
        uuid session_id FK
        string file_id FK
        string feature_name
        float processing_time
        float cost
    }
```

### Module Dependencies

```mermaid
graph TB
    subgraph CLI
        cli[src/cli.py]
    end

    subgraph Scripts
        foc[file_organizer_content_based.py]
        icr[image_content_renamer.py]
        ica[image_content_analyzer.py]
    end

    subgraph Core
        gen[generators.py]
        err[error_tracking.py]
        cost[cost_roi_calculator.py]
    end

    subgraph Storage
        gs[graph_store.py]
        models[models.py]
    end

    subgraph External
        torch[PyTorch/CLIP]
        tess[Tesseract]
        sentry[Sentry SDK]
        sa[SQLAlchemy]
    end

    cli --> foc
    foc --> gen & err & cost & gs
    icr & ica --> torch
    gs --> models --> sa
    err --> sentry
    foc --> torch & tess
```

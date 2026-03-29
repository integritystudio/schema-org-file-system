# Schema.org Alignment Analysis
## Schema-org-file-system Codebase Types vs. Schema.org Canonical Types

**Generated:** 2026-03-24
**Analysis Scope:** Core model types from `src/storage/models.py` and `src/base.py`

---

## 1. File → DigitalDocument / CreativeWork

**Recommended Type:** `DigitalDocument` (default); subtype selected by MIME

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `filename` | `name` | Primary title/name |
| `mime_type` | `encodingFormat` | MIME type |
| `file_size` | `contentSize` | Size in bytes |
| `created_at` | `dateCreated` | ISO 8601 |
| `modified_at` | `dateModified` | ISO 8601 |
| `original_path` | `url` | File path/URI |
| `extracted_text` | `text` / `description` | Extracted content |
| `schema_type` | used to select `@type` | Determines schema.org type |

---

## 2. Category → DefinedTerm

**Recommended Type:** `DefinedTerm` (controlled vocabulary term)

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Category name |
| `full_path` | `identifier` | Hierarchical path |
| `description` | `definition` | Category description |
| `parent_id` | `broader` | Parent category link |
| `level` | custom `hierarchyLevel` | Tree depth |
| `file_count` | custom `fileCount` | Statistics |
| `icon` | custom `icon` | Visual representation |
| `color` | custom `color` | Color styling |

---

## 3. Company → Organization

**Recommended Type:** `Organization`

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Organization name |
| `domain` | `url` | Primary website |
| `industry` | `knowsAbout` | Industry/sector |
| `file_count` | custom `mentionCount` | Reference count |
| `first_seen` | custom `firstMentionDate` | Temporal data |
| `last_seen` | custom `lastMentionDate` | Temporal data |

---

## 4. Person → Person

**Recommended Type:** `Person` (direct 1:1 match)

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Full name |
| `email` | `email` | Email address |
| `role` | `jobTitle` | Job role/position |
| `file_count` | custom `mentionCount` | Reference count |
| `first_seen` | custom `firstMentionDate` | When first encountered |
| `last_seen` | custom `lastMentionDate` | Most recent mention |

---

## 5. Location → Place

**Recommended Type:** `Place`; subtypes `City` / `Country` / `AdministrativeArea` by specificity

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Location name |
| `city` | `address.addressLocality` | City |
| `state` | `address.addressRegion` | State/province |
| `country` | `address.addressCountry` | Country |
| `latitude` | `geo.latitude` | GPS latitude |
| `longitude` | `geo.longitude` | GPS longitude |
| `geohash` | custom `geoHash` | Spatial index |
| `file_count` | custom `mentionCount` | Reference count |

---

## 6. Relationships

| Relationship | Property | Notes |
|---|---|---|
| File → Category | `about` | DefinedTerm reference |
| File → Company | `mentions` | Organization reference |
| File → Person | `author` or `mentions` | Person reference |
| File → Location | `spatialCoverage` | Place reference |
| Person → Company | `worksFor` | Organization reference |
| Person → Location | `workLocation` | Place reference |

All relationships use `@id` references only (no inline embedding).

---

## 7. Schema.org Context

Minimal:
```json
{ "@context": "https://schema.org" }
```

Extended (with custom properties):
```json
{
  "@context": [
    "https://schema.org",
    {
      "fileCount": "https://example.com/vocab/fileCount",
      "mentionCount": "https://example.com/vocab/mentionCount",
      "geoHash": "https://example.com/vocab/geoHash"
    }
  ]
}
```

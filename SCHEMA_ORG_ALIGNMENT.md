# Schema.org Alignment Analysis
## Schema-org-file-system Codebase Types vs. Schema.org Canonical Types

**Generated:** 2026-03-24
**Analysis Scope:** Core model types from `src/storage/models.py` and `src/base.py`

---

## Executive Summary

The schema-org-file-system project defines 5 core entity types that require alignment with schema.org canonical types. This analysis provides:

- Direct mappings to schema.org types
- Property alignment recommendations
- JSON-LD serialization patterns
- Implementation examples

---

## 1. File → DigitalDocument / CreativeWork

### Codebase Definition

```python
class File(Base):
    """Digital file with metadata"""
    id: String (SHA256)                    # Unique identifier
    filename: String                        # Original filename
    mime_type: String                       # MIME type (e.g., "application/pdf")
    file_size: Integer                      # Size in bytes
    file_extension: String                  # Extension (e.g., ".pdf", ".jpg")
    created_at: DateTime                    # Creation timestamp
    modified_at: DateTime                   # Last modification
    organized_at: DateTime                  # Organization timestamp
    extracted_text: Text                    # Extracted text content
    schema_type: String                     # Schema.org type (e.g., "ScholarlyArticle")
    schema_data: JSON                       # Full schema.org metadata
    image_*: Fields                         # Image-specific metadata
    status: Enum (PENDING|ORGANIZED|...)    # File processing status
```

### Recommended Schema.org Type: **DigitalDocument**

**Primary Mapping:**
```json
{
  "@context": "https://schema.org",
  "@type": "DigitalDocument",
  "@id": "urn:sha256:...",
  "name": "filename.pdf",
  "dateCreated": "2026-03-24T00:00:00Z",
  "dateModified": "2026-03-24T01:00:00Z",
  "encodingFormat": "application/pdf",
  "contentSize": "1024000",
  "url": "file:///path/to/file"
}
```

**Alternative Mappings (by file type):**
- `ScholarlyArticle` - For academic papers, research documents
- `NewsArticle` - For news items
- `BlogPosting` - For blog posts
- `SoftwareSourceCode` - For code files
- `MediaObject` - For media files (images, videos, audio)
- `ImageObject` - For image files
- `VideoObject` - For video files
- `AudioObject` - For audio files

### Property Alignment

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `filename` | `name` | Primary title/name of the document |
| `mime_type` | `encodingFormat` | MIME type as per schema.org spec |
| `file_size` | `contentSize` | Size in bytes |
| `created_at` | `dateCreated` | ISO 8601 DateTime |
| `modified_at` | `dateModified` | ISO 8601 DateTime |
| `original_path` | `url` or custom property | File path/URI |
| `extracted_text` | `text` or `description` | Extracted content |
| `schema_type` | USED TO SELECT @type | Determines which schema.org type to use |

### Implementation Pattern

```python
def to_schema_org(self) -> Dict[str, Any]:
    """Convert File to schema.org JSON-LD"""

    # Select appropriate type based on mime_type or explicit schema_type
    type_mapping = {
        'application/pdf': 'DigitalDocument',
        'image/jpeg': 'ImageObject',
        'image/png': 'ImageObject',
        'video/mp4': 'VideoObject',
        'audio/mpeg': 'AudioObject',
        'text/plain': 'DigitalDocument',
    }

    schema_type = self.schema_type or type_mapping.get(self.mime_type or '', 'DigitalDocument')

    return {
        "@context": "https://schema.org",
        "@type": schema_type,
        "@id": self.get_iri(),
        "name": self.filename,
        "dateCreated": self.created_at.isoformat() if self.created_at else None,
        "dateModified": self.modified_at.isoformat() if self.modified_at else None,
        "encodingFormat": self.mime_type,
        "contentSize": str(self.file_size) if self.file_size else None,
        "url": self.original_path,
        "text": self.extracted_text[:1000] if self.extracted_text else None,  # Truncate
        "isPartOf": [
            {
                "@type": "Dataset",
                "@id": f"urn:uuid:{self.session_id}"
            }
        ] if self.session_id else None
    }
```

---

## 2. Category → Intangible

### Codebase Definition

```python
class Category(Base):
    """Hierarchical file classification"""
    id: Integer                     # Internal ID
    canonical_id: UUID              # Public JSON-LD @id
    name: String                    # Category name (e.g., "Legal")
    parent_id: Integer              # Parent category (for hierarchy)
    level: Integer                  # Depth in hierarchy
    full_path: String               # Path string (e.g., "Legal/Contracts")
    file_count: Integer             # Number of files
    description: Text               # Description
    icon: String                    # Icon/emoji
    color: String                   # Hex color
```

### Recommended Schema.org Type: **Thing** (base type for taxonomy)

**Alternative Interpretations:**
- **`Intangible`** - If treating as abstract category
- **`DefinedTerm`** - If treating as controlled vocabulary term (recommended for clarity)
- **`Class`** - If modeling as RDF class

**Primary Mapping (using DefinedTerm):**
```json
{
  "@context": "https://schema.org",
  "@type": "DefinedTerm",
  "@id": "urn:uuid:...",
  "name": "Legal/Contracts",
  "identifier": "legal-contracts",
  "definition": "Legal documents and contracts",
  "url": "https://example.com/categories/legal-contracts",
  "color": "#ff0000",
  "inDefinedTermSet": {
    "@type": "DefinedTermSet",
    "name": "File Categories"
  },
  "broader": {
    "@type": "DefinedTerm",
    "@id": "urn:uuid:...",
    "name": "Legal"
  }
}
```

### Property Alignment

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Category name |
| `full_path` | `identifier` | Hierarchical path as identifier |
| `description` | `definition` | Category description |
| `parent_id` | `broader` | Parent category (using broader/narrower) |
| `level` | Custom property | Tree depth |
| `file_count` | Custom property `fileCount` | Statistics |
| `icon` | Custom property `icon` | Visual representation |
| `color` | Custom property `color` | Color styling |

### Implementation Pattern

```python
def to_schema_org(self) -> Dict[str, Any]:
    """Convert Category to schema.org JSON-LD"""
    return {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        "@id": self.get_iri(),
        "name": self.name,
        "identifier": self.full_path.lower().replace('/', '-'),
        "definition": self.description or f"Category: {self.name}",
        "inDefinedTermSet": {
            "@type": "DefinedTermSet",
            "@id": "urn:uuid:categories-taxonomy",
            "name": "File Organization Categories"
        },
        "broader": {
            "@type": "DefinedTerm",
            "@id": f"urn:uuid:{self.parent.canonical_id}"
        } if self.parent else None,
        # Custom extensions
        "fileCount": self.file_count,
        "hierarchyLevel": self.level,
        "icon": self.icon,
        "color": self.color
    }
```

---

## 3. Company → Organization

### Codebase Definition

```python
class Company(Base):
    """Organization entity detected in files"""
    id: Integer                     # Internal ID
    canonical_id: UUID              # Public JSON-LD @id
    name: String                    # Company name
    normalized_name: String         # Lowercase variant
    domain: String                  # Website domain (e.g., "example.com")
    industry: String                # Industry classification
    file_count: Integer             # Files mentioning this company
    first_seen: DateTime            # First mention
    last_seen: DateTime             # Last mention
```

### Recommended Schema.org Type: **Organization**

**Alternative Mappings:**
- `Corporation` - If known to be a corporation
- `LocalBusiness` - If location-specific business
- `NewsMediaOrganization` - If media company

**Primary Mapping:**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "urn:uuid:...",
  "name": "Example Company",
  "url": "https://example.com",
  "sameAs": [
    "https://example.com",
    "https://www.crunchbase.com/organization/..."
  ],
  "knowsAbout": "Technology",
  "foundingDate": "2020-01-01",
  "dateCreated": "2026-01-15T00:00:00Z",
  "dateModified": "2026-03-24T00:00:00Z"
}
```

### Property Alignment

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Organization name |
| `domain` | `url` | Primary website |
| `industry` | `knowsAbout` or `industryType` | Industry/sector |
| `file_count` | Custom property `mentionCount` | Reference count |
| `first_seen` | Custom property `firstMentionDate` | Temporal data |
| `last_seen` | Custom property `lastMentionDate` | Temporal data |

### Implementation Pattern

```python
def to_schema_org(self) -> Dict[str, Any]:
    """Convert Company to schema.org JSON-LD"""
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": self.get_iri(),
        "name": self.name,
        "url": f"https://{self.domain}" if self.domain else None,
        "sameAs": [
            f"https://{self.domain}",
            f"https://www.crunchbase.com/organization/{self.normalized_name}"
        ] if self.domain else None,
        "knowsAbout": self.industry or "Business",
        "dateFounded": self.first_seen.date().isoformat() if self.first_seen else None,
        # Metadata
        "dateCreated": self.first_seen.isoformat() if self.first_seen else None,
        "dateModified": self.last_seen.isoformat() if self.last_seen else None,
        # Custom tracking
        "mentionCount": self.file_count,
        "mentionSources": self.file_count
    }
```

---

## 4. Person → Person

### Codebase Definition

```python
class Person(Base):
    """Individual entity detected in files"""
    id: Integer                     # Internal ID
    canonical_id: UUID              # Public JSON-LD @id
    name: String                    # Full name
    normalized_name: String         # Lowercase variant
    email: String                   # Email address
    role: String                    # Job role/title
    file_count: Integer             # Files mentioning this person
    first_seen: DateTime            # First mention
    last_seen: DateTime             # Last mention
```

### Recommended Schema.org Type: **Person**

**Direct 1:1 Alignment** — This is a perfect match with schema.org's Person type.

**Primary Mapping:**
```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "@id": "urn:uuid:...",
  "name": "Jane Doe",
  "email": "jane@example.com",
  "jobTitle": "Senior Engineer",
  "knowsAbout": ["TypeScript", "React", "Node.js"],
  "workLocation": {
    "@type": "Place",
    "@id": "urn:uuid:location-..."
  },
  "worksFor": {
    "@type": "Organization",
    "@id": "urn:uuid:company-..."
  },
  "dateCreated": "2026-01-15T00:00:00Z",
  "dateModified": "2026-03-24T00:00:00Z"
}
```

### Property Alignment

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Full name |
| `email` | `email` | Email address |
| `role` | `jobTitle` | Job role/position |
| `file_count` | Custom property `mentionCount` | Reference count |
| `first_seen` | Custom property `firstMentionDate` | When first encountered |
| `last_seen` | Custom property `lastMentionDate` | Most recent mention |

### Implementation Pattern

```python
def to_schema_org(self) -> Dict[str, Any]:
    """Convert Person to schema.org JSON-LD"""
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": self.get_iri(),
        "name": self.name,
        "email": self.email,
        "jobTitle": self.role or "Unknown",
        # Relationships (if available)
        "worksFor": self.get_organization_reference(),
        "workLocation": self.get_location_reference(),
        # Temporal data
        "dateCreated": self.first_seen.isoformat() if self.first_seen else None,
        "dateModified": self.last_seen.isoformat() if self.last_seen else None,
        # Custom tracking
        "mentionCount": self.file_count,
        "mentionSources": self.file_count
    }
```

---

## 5. Location → Place

### Codebase Definition

```python
class Location(Base):
    """Geographic location entity"""
    id: Integer                     # Internal ID
    canonical_id: UUID              # Public JSON-LD @id
    name: String                    # Location name
    city: String                    # City name
    state: String                   # State/province
    country: String                 # Country
    latitude: Float                 # GPS latitude
    longitude: Float                # GPS longitude
    geohash: String                 # Geohash for spatial queries
    file_count: Integer             # Files mentioning this location
```

### Recommended Schema.org Type: **Place**

**Sub-type Alternatives:**
- `AdministrativeArea` - For cities, states, countries
- `City` - Specifically for cities
- `Country` - Specifically for countries

**Primary Mapping:**
```json
{
  "@context": "https://schema.org",
  "@type": "Place",
  "@id": "urn:uuid:...",
  "name": "San Francisco, California, USA",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "",
    "addressLocality": "San Francisco",
    "addressRegion": "California",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "geoHash": "9q8yy",
  "dateCreated": "2026-01-15T00:00:00Z"
}
```

### Property Alignment

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Location name |
| `city` | `address.addressLocality` | City in postal address |
| `state` | `address.addressRegion` | State/province |
| `country` | `address.addressCountry` | Country code or name |
| `latitude` | `geo.latitude` | GPS latitude |
| `longitude` | `geo.longitude` | GPS longitude |
| `geohash` | Custom property `geoHash` | Spatial index |
| `file_count` | Custom property `mentionCount` | Reference count |

### Implementation Pattern

```python
def to_schema_org(self) -> Dict[str, Any]:
    """Convert Location to schema.org JSON-LD"""
    return {
        "@context": "https://schema.org",
        "@type": "Place",
        "@id": self.get_iri(),
        "name": self.name,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": self.city,
            "addressRegion": self.state,
            "addressCountry": self.country
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": self.latitude,
            "longitude": self.longitude
        } if self.latitude and self.longitude else None,
        # Custom extension
        "geoHash": self.geohash,
        "mentionCount": self.file_count
    }
```

---

## 6. Relationships & Connections

### File ↔ Category Relationship

```json
{
  "@context": "https://schema.org",
  "@type": "DigitalDocument",
  "@id": "urn:sha256:...",
  "name": "contract.pdf",
  "about": [
    {
      "@type": "DefinedTerm",
      "@id": "urn:uuid:category-legal-contracts",
      "name": "Legal/Contracts"
    }
  ]
}
```

### File ↔ Company Relationship

```json
{
  "@context": "https://schema.org",
  "@type": "DigitalDocument",
  "@id": "urn:sha256:...",
  "mentions": [
    {
      "@type": "Organization",
      "@id": "urn:uuid:company-...",
      "name": "Acme Corp"
    }
  ]
}
```

### File ↔ Person Relationship

```json
{
  "@context": "https://schema.org",
  "@type": "DigitalDocument",
  "@id": "urn:sha256:...",
  "author": {
    "@type": "Person",
    "@id": "urn:uuid:person-...",
    "name": "Jane Doe"
  },
  "mentions": [
    {
      "@type": "Person",
      "@id": "urn:uuid:person-...",
      "name": "John Smith"
    }
  ]
}
```

### File ↔ Location Relationship

```json
{
  "@context": "https://schema.org",
  "@type": "DigitalDocument",
  "@id": "urn:sha256:...",
  "spatialCoverage": {
    "@type": "Place",
    "@id": "urn:uuid:location-...",
    "name": "San Francisco, CA"
  }
}
```

---

## 7. Implementation Checklist

### In `src/storage/models.py`:

- [ ] Add `to_schema_org()` method to each model class
- [ ] Implement proper `@id` (IRI) generation using canonical IDs
- [ ] Add property mapping for all schema.org fields
- [ ] Handle relationships between entities
- [ ] Add custom properties for non-standard fields
- [ ] Ensure datetime serialization to ISO 8601 format

### In `src/base.py` (SchemaOrgBase):

- [ ] Extend helper methods to support all 5 entity types
- [ ] Add type-specific validation
- [ ] Implement relationship building methods
- [ ] Add nested object support for Address, GeoCoordinates, etc.

### Integration Points:

- [ ] REST API endpoints return proper schema.org JSON-LD
- [ ] Database models serialize to schema.org format
- [ ] Search endpoints include schema.org context
- [ ] Performance impact analysis includes schema.org metrics

---

## 8. Schema.org Context

All JSON-LD should use:

```json
{
  "@context": "https://schema.org",
  "@vocab": "https://schema.org/"
}
```

For extended contexts:

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

---

## 9. References

- **Schema.org Documentation**: https://schema.org/docs/documents.html
- **DigitalDocument**: https://schema.org/DigitalDocument
- **DefinedTerm**: https://schema.org/DefinedTerm
- **Organization**: https://schema.org/Organization
- **Person**: https://schema.org/Person
- **Place**: https://schema.org/Place
- **JSON-LD Specification**: https://www.w3.org/TR/json-ld11/

---

## 10. Next Steps

1. **Implement to_schema_org() methods** in each model class
2. **Add comprehensive tests** for schema.org serialization
3. **Validate against schema.org validator**: https://validator.schema.org/
4. **Create JSON-LD examples** for documentation
5. **Measure schema.org impact** on SEO and LLM understanding
6. **Update API documentation** with schema.org examples

# Schema.org Alignment — Quick Reference

## Type Mappings Summary

### 1. File ↔ DigitalDocument/CreativeWork

```
Codebase Type: File
├─ Primary Schema.org Type: DigitalDocument
├─ Subtypes by MIME:
│  ├─ image/* → ImageObject
│  ├─ video/* → VideoObject
│  ├─ audio/* → AudioObject
│  ├─ application/pdf → DigitalDocument
│  ├─ text/html → WebPage
│  ├─ text/markdown → DigitalDocument
│  └─ text/* → DigitalDocument
├─ Key Properties:
│  ├─ filename → name
│  ├─ mime_type → encodingFormat
│  ├─ file_size → contentSize
│  ├─ created_at → dateCreated
│  ├─ modified_at → dateModified
│  ├─ extracted_text → text
│  └─ original_path → url
└─ IRI Pattern: urn:sha256:{sha256_hash}
```

**Canonical @type Selection Algorithm:**
```
if mime_type starts with 'image/' → ImageObject
else if mime_type starts with 'video/' → VideoObject
else if mime_type starts with 'audio/' → AudioObject
else if explicit schema_type set → use that
else → DigitalDocument (default)
```

### 2. Category ↔ DefinedTerm

```
Codebase Type: Category
├─ Primary Schema.org Type: DefinedTerm
├─ Alternative: Intangible
├─ Key Properties:
│  ├─ name → name
│  ├─ full_path → identifier (hierarchical ID)
│  ├─ description → definition
│  ├─ parent_id → broader (link to parent)
│  ├─ level → custom hierarchyLevel
│  ├─ file_count → custom fileCount
│  ├─ icon → custom icon
│  └─ color → custom color
└─ IRI Pattern: urn:uuid:{uuid_v5_from_name}
```

**Hierarchy Linking:**
- Parent category in `broader` property
- Child categories in `narrower` property
- Taxonomy root in `inDefinedTermSet`

### 3. Company ↔ Organization

```
Codebase Type: Company
├─ Primary Schema.org Type: Organization
├─ Subtypes:
│  ├─ Corporation (if company type known)
│  ├─ LocalBusiness (if location-specific)
│  └─ NewsMediaOrganization (if media)
├─ Key Properties:
│  ├─ name → name
│  ├─ domain → url
│  ├─ industry → knowsAbout
│  ├─ first_seen → dateFounded
│  ├─ file_count → custom mentionCount
│  └─ file_count → custom mentionSources
└─ IRI Pattern: urn:uuid:{uuid_v5_from_name}
```

**External Links:**
- `sameAs`: Link to external profiles (Crunchbase, Wikipedia, etc.)
- `url`: Primary website URL

### 4. Person ↔ Person

```
Codebase Type: Person
├─ Primary Schema.org Type: Person (perfect 1:1 match!)
├─ Key Properties:
│  ├─ name → name
│  ├─ email → email
│  ├─ role → jobTitle
│  ├─ first_seen → custom firstMentionDate
│  └─ file_count → custom mentionCount
├─ Optional Properties:
│  ├─ worksFor → Organization
│  ├─ workLocation → Place
│  └─ knowsAbout → [skills/topics]
└─ IRI Pattern: urn:uuid:{uuid_v5_from_name}
```

**Relationship Linking:**
- `worksFor`: Link to Company (Organization)
- `workLocation`: Link to Location (Place)
- `affiliateOf`: Secondary affiliations

### 5. Location ↔ Place

```
Codebase Type: Location
├─ Primary Schema.org Type: Place
├─ Specialized Subtypes:
│  ├─ City (if only city specified)
│  ├─ Country (if only country specified)
│  └─ AdministrativeArea
├─ Key Properties:
│  ├─ name → name
│  ├─ city → address.addressLocality
│  ├─ state → address.addressRegion
│  ├─ country → address.addressCountry
│  ├─ latitude → geo.latitude
│  ├─ longitude → geo.longitude
│  └─ geohash → custom geoHash
└─ IRI Pattern: urn:uuid:{uuid_v5_from_name}
```

**Nested Objects:**
- `address` (PostalAddress) - Structured address fields
- `geo` (GeoCoordinates) - Precise location coordinates

---

## Property Type Mappings

| Codebase Type | Schema.org Type | Inheritance Chain |
|---|---|---|
| File | DigitalDocument | CreativeWork → Thing |
| File | ImageObject | MediaObject → CreativeWork → Thing |
| File | VideoObject | MediaObject → CreativeWork → Thing |
| Category | DefinedTerm | Intangible → Thing |
| Company | Organization | Thing |
| Company | Corporation | Organization → Thing |
| Person | Person | Thing |
| Location | Place | Thing |
| Location | City | Place → Thing |

---

## @id Generation Strategies

### File (SHA256 Hash)
```
canonical_id = f"urn:sha256:{SHA256(file_path)}"
@id = canonical_id

// Example:
@id: urn:sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### Category, Company, Person, Location (UUID v5)
```
canonical_id = str(uuid.uuid5(namespace_uuid, normalized_name))
@id = f"urn:uuid:{canonical_id}"

// Namespaces:
category_ns = UUID('c4e8a9c0-2345-6789-abcd-ef0123456789')
company_ns  = UUID('c0e1a2b3-4567-89ab-cdef-012345678901')
person_ns   = UUID('d1e2a3b4-5678-9abc-def0-123456789012')
location_ns = UUID('e2e3a4b5-6789-abcd-ef01-234567890123')

// Example:
@id: urn:uuid:c4e8a9c0-2345-6789-abcd-ef0123456789
```

---

## JSON-LD Context

### Minimal (schema.org only)
```json
{
  "@context": "https://schema.org"
}
```

### Extended (with custom properties)
```json
{
  "@context": [
    "https://schema.org",
    {
      "fileCount": "https://example.com/vocab/fileCount",
      "mentionCount": "https://example.com/vocab/mentionCount",
      "mentionSources": "https://example.com/vocab/mentionSources",
      "hierarchyLevel": "https://example.com/vocab/hierarchyLevel",
      "geoHash": "https://example.com/vocab/geoHash",
      "icon": "https://example.com/vocab/icon",
      "color": "https://example.com/vocab/color"
    }
  ]
}
```

---

## Validation Checklist

### For Each Type Implementation

- [ ] Has `to_schema_org()` method
- [ ] Returns properly formatted JSON-LD with @context and @type
- [ ] Includes @id with correct IRI format
- [ ] Maps all primary properties
- [ ] Handles NULL/missing values gracefully
- [ ] Dates serialized as ISO 8601 strings
- [ ] Uses correct canonical_id for @id
- [ ] Relationships link to other entities by @id
- [ ] Custom properties namespaced appropriately
- [ ] Validates against schema.org validator

### For Relationships

- [ ] File→Category via `about` property
- [ ] File→Company via `mentions` property
- [ ] File→Person via `author` or `mentions` property
- [ ] File→Location via `spatialCoverage` property
- [ ] Person→Company via `worksFor` property
- [ ] Person→Location via `workLocation` property
- [ ] All relationships use @id references only

---

## Example Usage

### Converting a File to Schema.org

```python
file = session.query(File).filter_by(id='abc123').first()
schema_org_data = file.to_schema_org()

# Output:
{
  "@context": "https://schema.org",
  "@type": "DigitalDocument",
  "@id": "urn:sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "name": "contract.pdf",
  "dateCreated": "2026-03-24T10:00:00Z",
  "dateModified": "2026-03-24T11:00:00Z",
  "encodingFormat": "application/pdf",
  "contentSize": "102400",
  "url": "/path/to/contract.pdf",
  "about": [
    {
      "@type": "DefinedTerm",
      "@id": "urn:uuid:c4e8a9c0-2345-6789-abcd-ef0123456789",
      "name": "Legal/Contracts"
    }
  ],
  "mentions": [
    {
      "@type": "Organization",
      "@id": "urn:uuid:c0e1a2b3-4567-89ab-cdef-012345678901",
      "name": "Acme Corp"
    },
    {
      "@type": "Person",
      "@id": "urn:uuid:d1e2a3b4-5678-9abc-def0-123456789012",
      "name": "Jane Doe"
    }
  ],
  "spatialCoverage": {
    "@type": "Place",
    "@id": "urn:uuid:e2e3a4b5-6789-abcd-ef01-234567890123",
    "name": "San Francisco, CA"
  }
}
```

---

## Schema.org Validator

Test your JSON-LD output at:
**https://validator.schema.org/**

Paste your JSON-LD and verify:
- ✅ Correct @type selection
- ✅ All required properties present
- ✅ Valid property values
- ✅ Proper nesting of objects
- ✅ No schema warnings

---

## Resources

- [Schema.org Type Hierarchy](https://schema.org/docs/schemas.html)
- [JSON-LD Playground](https://json-ld.org/playground/)
- [Schema.org Validator](https://validator.schema.org/)
- [RDF to JSON-LD Converter](https://rdf.js.org/playground/)

---

## Custom Property Namespace

For properties not in schema.org, define a custom namespace:

```
Example namespace URL: https://example.com/vocab/

Properties:
- https://example.com/vocab/fileCount
- https://example.com/vocab/mentionCount
- https://example.com/vocab/hierarchyLevel
- https://example.com/vocab/geoHash
```

Register namespace in @context for proper semantic meaning.

---

**Last Updated:** 2026-03-24
**Document Version:** 1.0
**Alignment Status:** Complete for 5 core entity types

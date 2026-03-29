# Schema.org Architecture Reference

**Scope:** Core model types in `src/storage/models.py` and `src/storage/schema_org_base.py`

---

## Type Mappings

| Codebase Type | Schema.org Type | Inheritance Chain |
|---|---|---|
| File | DigitalDocument | CreativeWork → Thing |
| File | ImageObject | MediaObject → CreativeWork → Thing |
| File | VideoObject | MediaObject → CreativeWork → Thing |
| File | AudioObject | MediaObject → CreativeWork → Thing |
| File | WebPage | CreativeWork → Thing |
| Category | DefinedTerm | Intangible → Thing |
| Company | Organization | Thing |
| Company | Corporation | Organization → Thing |
| Person | Person | Thing |
| Location | Place | Thing |
| Location | City | Place → Thing |

---

## Entity Details

### File → DigitalDocument / MediaObject

**Type selection algorithm:**
```
if mime_type starts with 'image/' → ImageObject
if mime_type starts with 'video/' → VideoObject
if mime_type starts with 'audio/' → AudioObject
if mime_type == 'text/html'       → WebPage
if schema_type set explicitly     → use that
else                              → DigitalDocument
```

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `filename` | `name` | Primary title |
| `mime_type` | `encodingFormat` | MIME type string |
| `file_size` | `contentSize` | Bytes as string |
| `created_at` | `dateCreated` | ISO 8601 |
| `modified_at` | `dateModified` | ISO 8601 |
| `original_path` | `url` | File path/URI |
| `extracted_text` | `text` | Truncated to 2000 chars |
| `image_width` | `width` | ImageObject only |
| `image_height` | `height` | ImageObject only |
| `exif_datetime` | `datePublished` | ImageObject only |
| `gps_latitude/longitude` | `contentLocation.geo` | ImageObject only |

**IRI:** `urn:sha256:{sha256_hash}`

---

### Category → DefinedTerm

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Category name |
| `full_path` | `identifier` | Hierarchical path |
| `description` | `definition` | Fallback: `"Category: {name}"` |
| `parent_id` | `broader` | Link to parent DefinedTerm |
| `subcategories` | `narrower` | Links to child DefinedTerms |
| — | `inDefinedTermSet` | Fixed: `urn:uuid:categories-taxonomy` |
| `level` | `hierarchyLevel` | custom |
| `file_count` | `fileCount` | custom |
| `icon` | `icon` | custom |
| `color` | `color` | custom |

**IRI:** `urn:uuid:{uuid_v5(category_ns, normalized_name)}`
`category_ns = UUID('c4e8a9c0-2345-6789-abcd-ef0123456789')`

---

### Company → Organization

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Organization name |
| `domain` | `url` | Normalized to `https://` prefix |
| `industry` | `knowsAbout` | Industry/sector string |
| `first_seen` | `dateCreated` | ISO 8601 |
| `last_seen` | `dateModified` | ISO 8601 |
| `domain` | `sameAs` | External reference array |
| `file_count` | `mentionCount` | custom |

**IRI:** `urn:uuid:{uuid_v5(company_ns, normalized_name)}`
`company_ns = UUID('c0e1a2b3-4567-89ab-cdef-012345678901')`

---

### Person → Person

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Full name |
| `email` | `email` | Email address |
| `role` | `jobTitle` | Job role/position |
| `first_seen` | `dateCreated` | ISO 8601 |
| `last_seen` | `dateModified` | ISO 8601 |
| `file_count` | `mentionCount` | custom |
| — | `worksFor` | Organization @id ref (optional) |
| — | `workLocation` | Place @id ref (optional) |

**IRI:** `urn:uuid:{uuid_v5(person_ns, normalized_name)}`
`person_ns = UUID('d1e2a3b4-5678-9abc-def0-123456789012')`

---

### Location → Place

**Type selection:** `Place` (full address) → `City` (city present) → `Country` (country only)

| Codebase Property | Schema.org Property | Notes |
|---|---|---|
| `name` | `name` | Location name |
| `city` | `address.addressLocality` | Nested PostalAddress |
| `state` | `address.addressRegion` | Nested PostalAddress |
| `country` | `address.addressCountry` | 2-char ISO code |
| `latitude` | `geo.latitude` | Nested GeoCoordinates |
| `longitude` | `geo.longitude` | Nested GeoCoordinates |
| `geohash` | `geoHash` | custom |
| `file_count` | `mentionCount` | custom |

**IRI:** `urn:uuid:{uuid_v5(location_ns, normalized_name)}`
`location_ns = UUID('e2e3a4b5-6789-abcd-ef01-234567890123')`

---

## Relationships

All relationships use `@id` references only — no inline embedding.

| Relationship | Property | Notes |
|---|---|---|
| File → Category | `about` | Array of DefinedTerm refs |
| File → Company | `mentions` | Array of Organization refs |
| File → Person | `mentions` | Array of Person refs |
| File → Location | `spatialCoverage` | Place ref (scalar or array) |
| Person → Company | `worksFor` | Organization ref |
| Person → Location | `workLocation` | Place ref |
| Category → parent | `broader` | DefinedTerm ref |
| Category → children | `narrower` | Array of DefinedTerm refs |

---

## JSON-LD Context

**Minimal:**
```json
{ "@context": "https://schema.org" }
```

**Extended (with custom properties):**
```json
{
  "@context": [
    "https://schema.org",
    {
      "fileCount":      "https://example.com/vocab/fileCount",
      "mentionCount":   "https://example.com/vocab/mentionCount",
      "mentionSources": "https://example.com/vocab/mentionSources",
      "hierarchyLevel": "https://example.com/vocab/hierarchyLevel",
      "geoHash":        "https://example.com/vocab/geoHash",
      "icon":           "https://example.com/vocab/icon",
      "color":          "https://example.com/vocab/color"
    }
  ]
}
```

Context document served at `GET /schema/context` via `src/storage/schema_org_context.py`.

---

## Implementation Examples

### File

```python
def get_iri(self) -> str:
    return self.canonical_id or f"urn:sha256:{self.id}"

def to_schema_org(self) -> Dict[str, Any]:
    schema_type = self.schema_type or self.get_schema_type_from_mime(self.mime_type)
    result = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "@id": self.get_iri(),
        "name": self.filename,
    }
    if self.created_at:   result["dateCreated"]    = self.created_at.isoformat()
    if self.modified_at:  result["dateModified"]   = self.modified_at.isoformat()
    if self.mime_type:    result["encodingFormat"]  = self.mime_type
    if self.file_size:    result["contentSize"]     = str(self.file_size)
    if self.original_path: result["url"]            = self.original_path
    if self.extracted_text: result["text"]          = self.extracted_text[:2000]

    if schema_type == "ImageObject":
        if self.image_width:   result["width"]  = self.image_width
        if self.image_height:  result["height"] = self.image_height
        if self.gps_latitude and self.gps_longitude:
            result["contentLocation"] = {
                "@type": "Place",
                "geo": {"@type": "GeoCoordinates",
                        "latitude": self.gps_latitude,
                        "longitude": self.gps_longitude}
            }

    result.update(self._build_relationships())
    return result

def _build_relationships(self) -> Dict[str, Any]:
    rel = {}
    if self.categories:
        rel["about"] = [{"@type": "DefinedTerm", "@id": c.get_iri(), "name": c.name}
                        for c in self.categories]
    mentions = (
        [{"@type": "Organization", "@id": c.get_iri(), "name": c.name} for c in self.companies] +
        [{"@type": "Person",       "@id": p.get_iri(), "name": p.name} for p in self.people]
    )
    if mentions:
        rel["mentions"] = mentions
    if self.locations:
        locs = [{"@type": "Place", "@id": l.get_iri(), "name": l.name} for l in self.locations]
        rel["spatialCoverage"] = locs[0] if len(locs) == 1 else locs
    return rel
```

### Category

```python
def get_iri(self) -> str:
    return f"urn:uuid:{self.canonical_id}" if self.canonical_id else f"urn:uuid:{self.id}"

def to_schema_org(self) -> Dict[str, Any]:
    result = {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        "@id": self.get_iri(),
        "name": self.name,
        "definition": self.description or f"Category: {self.name}",
        "inDefinedTermSet": {"@type": "DefinedTermSet",
                             "@id": "urn:uuid:categories-taxonomy",
                             "name": "File Organization Categories"},
        "fileCount": self.file_count or 0,
        "hierarchyLevel": self.level or 0,
    }
    if self.full_path:
        result["identifier"] = self.full_path.lower().replace('/', '-')
    if self.parent:
        result["broader"] = {"@type": "DefinedTerm", "@id": self.parent.get_iri(),
                             "name": self.parent.name}
    if self.subcategories:
        result["narrower"] = [{"@type": "DefinedTerm", "@id": s.get_iri(), "name": s.name}
                              for s in self.subcategories]
    if self.icon:  result["icon"]  = self.icon
    if self.color: result["color"] = self.color
    return result
```

### Company

```python
def to_schema_org(self) -> Dict[str, Any]:
    result = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": self.get_iri(),
        "name": self.name,
        "mentionCount": self.file_count or 0,
    }
    if self.domain:
        url = self.domain if self.domain.startswith(('http://', 'https://')) else f"https://{self.domain}"
        result["url"] = url
        result["sameAs"] = [url]
    if self.industry:   result["knowsAbout"]   = self.industry
    if self.first_seen: result["dateCreated"]  = self.first_seen.isoformat()
    if self.last_seen:  result["dateModified"] = self.last_seen.isoformat()
    return result
```

### Person

```python
def to_schema_org(self) -> Dict[str, Any]:
    result = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": self.get_iri(),
        "name": self.name,
        "mentionCount": self.file_count or 0,
    }
    if self.email:      result["email"]        = self.email
    if self.role:       result["jobTitle"]     = self.role
    if self.first_seen: result["dateCreated"]  = self.first_seen.isoformat()
    if self.last_seen:  result["dateModified"] = self.last_seen.isoformat()
    return result
```

### Location

```python
def infer_schema_type(self) -> str:
    if self.country and not self.state and not self.city: return "Country"
    if self.city: return "City"
    return "Place"

def to_schema_org(self) -> Dict[str, Any]:
    result = {
        "@context": "https://schema.org",
        "@type": self.infer_schema_type(),
        "@id": self.get_iri(),
        "name": self.name,
        "mentionCount": self.file_count or 0,
    }
    address = {}
    if self.city:    address["addressLocality"] = self.city
    if self.state:   address["addressRegion"]   = self.state
    if self.country: address["addressCountry"]  = self.country[:2]
    if address:
        result["address"] = {"@type": "PostalAddress", **address}
    if self.latitude is not None and self.longitude is not None:
        result["geo"] = {"@type": "GeoCoordinates",
                         "latitude": self.latitude, "longitude": self.longitude}
    if self.geohash:    result["geoHash"]     = self.geohash
    if self.created_at: result["dateCreated"] = self.created_at.isoformat()
    return result
```

---

## Validation Checklist

- [ ] `get_iri()` returns correct IRI pattern for the entity type
- [ ] `to_schema_org()` includes `@context`, `@type`, `@id`, `name`
- [ ] Dates serialized as ISO 8601 strings
- [ ] Relationships use `@id` refs only (no inline embedding)
- [ ] NULL / missing fields omitted (not serialized as `None`)
- [ ] Custom properties namespaced under `https://example.com/vocab/`
- [ ] Output passes [validator.schema.org](https://validator.schema.org/)

---

## Resources

- [Schema.org Type Hierarchy](https://schema.org/docs/schemas.html)
- [JSON-LD Playground](https://json-ld.org/playground/)
- [Schema.org Validator](https://validator.schema.org/)

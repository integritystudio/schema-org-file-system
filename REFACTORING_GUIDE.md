# Schema.org Refactoring Guide

## Overview

The schema.org implementation has been refactored to eliminate duplication and provide a cleaner API. This guide explains the new module structure and migration path.

## New Module Structure

### 1. `schema_org_base.py`
Base classes and mixins for schema.org serialization.

**Key Components:**
- `SchemaOrgSerializable` - Abstract base class requiring `get_iri()`, `get_schema_type()`, `to_schema_org()`
- `IriMixin` - Utilities for generating URN-based IRIs
- `PropertyBuilder` - Utilities for safely adding properties to JSON-LD objects
- `SCHEMA_ORG_CONTEXT` - Constant for schema.org context URL

**Usage:**
```python
from schema_org_base import SchemaOrgSerializable, PropertyBuilder

class File(Base, SchemaOrgSerializable):
    def get_iri(self) -> str:
        return f"urn:sha256:{self.id}"

    def get_schema_type(self) -> str:
        return "DigitalDocument"

    def to_schema_org(self) -> Dict[str, Any]:
        result = super().to_schema_org()  # Gets @context, @type, @id
        PropertyBuilder.add_if_present(result, "name", self.filename)
        PropertyBuilder.add_iso_datetime(result, "dateCreated", self.created_at)
        return result
```

### 2. `mime_mapping.py`
Maps MIME types to schema.org types deterministically.

**Key Class:**
- `MimeTypeMapper` - Static methods for MIME → schema.org type mapping

**Usage:**
```python
from mime_mapping import MimeTypeMapper

schema_type = MimeTypeMapper.get_schema_type("image/png")  # "ImageObject"
is_image = MimeTypeMapper.is_image("application/pdf")  # False
```

### 3. `schema_org_builders.py`
Factory functions for building common schema.org structures.

**Key Functions:**
- `build_entity_reference()` - Generic entity reference (@id, @type, name)
- `build_location_object()` - Complete Place with address and coordinates
- `build_image_metadata()` - Image-specific properties
- `build_entity_mentions()` - Mentions array from related entities
- `build_spatial_coverage()` - Single or multiple locations

**Usage:**
```python
from schema_org_builders import (
    build_organization_reference,
    build_image_metadata,
    build_entity_mentions
)

# In File.to_schema_org():
result = super().to_schema_org()

# Add company mentions
if self.companies:
    result["mentions"] = build_entity_mentions(companies=self.companies)

# Add image metadata
if self.mime_type and MimeTypeMapper.is_image(self.mime_type):
    result.update(build_image_metadata(
        width=self.image_width,
        height=self.image_height,
        has_faces=self.has_faces,
        latitude=self.gps_latitude,
        longitude=self.gps_longitude,
    ))
```

### 4. `schema_org_exporter.py`
Unified service for exporting entities to JSON-LD in various formats.

**Key Class:**
- `SchemaOrgExporter` - Handles batch export with multiple output formats

**Supported Formats:**
- `json` - Standard JSON with pretty-printing
- `ndjson` - Newline-delimited JSON (streaming)
- `@graph` - JSON-LD @graph structure (recommended for multiple entities)

**Usage:**
```python
from schema_org_exporter import SchemaOrgExporter

exporter = SchemaOrgExporter(session)

# Export all entity types to JSON file
exporter.export_to_file(
    output_path="export.json",
    entity_classes=[File, Category, Company, Person, Location],
    pretty=True
)

# Export as NDJSON (one entity per line)
exporter.export_to_ndjson(
    output_path="export.ndjson",
    entity_classes=[File, Company, Person]
)

# Export with @graph structure
exporter.export_with_graph(
    output_path="export-graph.json",
)
```

### 5. `schema_org_variants.py`
Alternative representations for entities in different contexts.

**Key Classes:**
- `CategoryVariants.to_defined_term()` - Category as DefinedTerm (recommended)
- `CategoryVariants.to_intangible()` - Simplified representation
- `PersonVariants.to_person_with_context()` - Person with relationships
- `FileVariants.to_creative_work()` - File as CreativeWork
- `FileVariants.to_media_object()` - File as media-specific type

**Usage:**
```python
from schema_org_variants import CategoryVariants

# Category as DefinedTerm (primary representation)
term = CategoryVariants.to_defined_term(
    canonical_id=category.canonical_id,
    name=category.name,
    description=category.description,
    full_path=category.full_path,
    parent_iri=category.parent.get_iri() if category.parent else None,
    children_iris={
        child.get_iri(): child.name
        for child in category.subcategories
    },
    file_count=category.file_count,
    icon=category.icon,
    color=category.color,
)

# Or simplified Intangible representation
intangible = CategoryVariants.to_intangible(
    canonical_id=category.canonical_id,
    name=category.name,
    description=category.description,
)
```

## Migration Path

### Step 1: Update Model Base Classes

```python
from schema_org_base import SchemaOrgSerializable, PropertyBuilder
from mime_mapping import MimeTypeMapper

class File(Base, SchemaOrgSerializable):
    # ... existing fields ...

    def get_iri(self) -> str:
        return self.canonical_id or f"urn:sha256:{self.id}"

    def get_schema_type(self) -> str:
        if self.schema_type:
            return self.schema_type
        return MimeTypeMapper.get_schema_type(self.mime_type)
```

### Step 2: Simplify to_schema_org() Methods

**Before:**
```python
def to_schema_org(self) -> Dict[str, Any]:
    result = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "@id": self.get_iri(),
        "name": self.filename,
    }

    if self.created_at:
        result["dateCreated"] = self.created_at.isoformat()
    # ... dozens more lines ...
```

**After:**
```python
def to_schema_org(self) -> Dict[str, Any]:
    result = super().to_schema_org()  # Handles @context, @type, @id

    PropertyBuilder.add_if_present(result, "name", self.filename)
    PropertyBuilder.add_iso_datetime(result, "dateCreated", self.created_at)

    # Use builder functions for complex structures
    if self.companies or self.people:
        result["mentions"] = build_entity_mentions(
            companies=self.companies,
            people=self.people
        )
```

### Step 3: Use Exporter for Bulk Operations

**Before:**
```python
# Manual iteration and JSON handling
for file in session.query(File).all():
    # ...
```

**After:**
```python
exporter = SchemaOrgExporter(session)
exporter.export_to_file("output.json")
```

### Step 4: Support Alternative Representations

```python
class Category(Base, SchemaOrgSerializable):
    def to_schema_org(self) -> Dict[str, Any]:
        """Primary representation as DefinedTerm"""
        from schema_org_variants import CategoryVariants
        return CategoryVariants.to_defined_term(
            canonical_id=self.canonical_id,
            name=self.name,
            # ...
        )

    def to_schema_org_as_intangible(self) -> Dict[str, Any]:
        """Alternative simplified representation"""
        from schema_org_variants import CategoryVariants
        return CategoryVariants.to_intangible(
            canonical_id=self.canonical_id,
            name=self.name,
            description=self.description,
        )
```

## Benefits

1. **Reduced Duplication**
   - `get_iri()` pattern extracted to mixins
   - `@context` constant centralized
   - Relationship building delegated to builders

2. **Better Maintainability**
   - Changes to schema.org pattern affect all classes automatically
   - MIME mapping in one place
   - Builders handle edge cases consistently

3. **Cleaner Model Code**
   - Models focus on their business logic
   - Schema.org serialization is delegated
   - Support for variants without bloating main methods

4. **Easier Testing**
   - Builder functions are pure and easily testable
   - Exporter has single responsibility
   - Variants can be tested independently

5. **Future-Proof**
   - Easy to add new builders for new relationship types
   - Variant system supports new context requirements
   - Exporter adaptable for new output formats

## Integration Checklist

- [x] Update File class with SchemaOrgSerializable
- [x] Update Category class with SchemaOrgSerializable
- [x] Update Company class with SchemaOrgSerializable
- [x] Update Person class with SchemaOrgSerializable
- [x] Update Location class with SchemaOrgSerializable
- [x] Replace manual MIME mapping with MimeTypeMapper
- [x] Simplify to_schema_org() methods using PropertyBuilder
- [x] Use builders for relationship properties
- [x] Replace bulk export functions with SchemaOrgExporter
- [x] Add variant representations for appropriate entities
- [x] Update REST API endpoints to use exporter
- [x] Add tests for new modules
- [x] Update documentation

## Next Steps

1. ~~Create unit tests for each new module~~ — done (`c2ad740`: `tests/test_schema_org_serialization.py`, 16 test methods covering all entities, relationships, MIME mapping, and JSON-LD validity)
2. ~~Implement integration tests showing end-to-end flow~~ — done (`d99e979`: Playwright + OpenTelemetry e2e tests added)
3. ~~Update REST API endpoints to use SchemaOrgExporter~~ — done (`c2ad740`: 15 FastAPI endpoints; `e989a88`: Pydantic `response_model=` on all endpoints with Depends() validation)
4. Add validation that exported JSON-LD is valid against schema.org — partial (tests assert structural JSON-LD validity; no external schema.org validator integration)
5. ~~Document property mappings in code comments~~ — done (`8b64fcf`: `ALIGNMENT_QUICK_REFERENCE.md`, `SCHEMA_ORG_ALIGNMENT.md`, `IMPLEMENTATION_EXAMPLES.md` added)
6. Consider JSON-LD context file generation for complex graphs — not started

---

**Version:** 1.2 (Next Steps Updated)
**Date:** 2026-03-28

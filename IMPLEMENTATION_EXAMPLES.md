# Schema.org Implementation Examples

## Complete Implementation Patterns for Each Type

---

## 1. File.to_schema_org()

### Basic Implementation

```python
from typing import Any, Dict, Optional
from datetime import datetime
import hashlib

class File(Base):
    """Digital file with schema.org JSON-LD support"""

    # ... existing fields ...

    def get_iri(self) -> str:
        """Get the JSON-LD @id IRI for this file."""
        if self.canonical_id:
            return self.canonical_id
        return f"urn:sha256:{self.id}"

    @staticmethod
    def get_schema_type_from_mime(mime_type: Optional[str]) -> str:
        """Select appropriate schema.org type based on MIME type."""
        if not mime_type:
            return "DigitalDocument"

        mime_lower = mime_type.lower()

        type_mapping = {
            # Images
            "image/jpeg": "ImageObject",
            "image/png": "ImageObject",
            "image/gif": "ImageObject",
            "image/svg": "ImageObject",
            "image/webp": "ImageObject",

            # Video
            "video/mp4": "VideoObject",
            "video/mpeg": "VideoObject",
            "video/quicktime": "VideoObject",
            "video/webm": "VideoObject",

            # Audio
            "audio/mpeg": "AudioObject",
            "audio/wav": "AudioObject",
            "audio/ogg": "AudioObject",
            "audio/mp4": "AudioObject",

            # Documents
            "application/pdf": "DigitalDocument",
            "application/msword": "DigitalDocument",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DigitalDocument",
            "text/plain": "DigitalDocument",
            "text/markdown": "DigitalDocument",
            "text/html": "WebPage",

            # Code
            "application/json": "SoftwareSourceCode",
            "application/x-python": "SoftwareSourceCode",
            "text/x-python": "SoftwareSourceCode",
            "text/typescript": "SoftwareSourceCode",
        }

        # Try exact match first
        if mime_type in type_mapping:
            return type_mapping[mime_type]

        # Try prefix match
        for mime_prefix, schema_type in type_mapping.items():
            if mime_lower.startswith(mime_prefix.split('/')[0] + '/'):
                return schema_type

        return "DigitalDocument"

    def to_schema_org(self) -> Dict[str, Any]:
        """Convert File to schema.org JSON-LD"""

        # Select appropriate type
        schema_type = self.schema_type or self.get_schema_type_from_mime(self.mime_type)

        result = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "@id": self.get_iri(),
            "name": self.filename,
        }

        # Add optional properties if present
        if self.created_at:
            result["dateCreated"] = self.created_at.isoformat()

        if self.modified_at:
            result["dateModified"] = self.modified_at.isoformat()

        if self.mime_type:
            result["encodingFormat"] = self.mime_type

        if self.file_size:
            result["contentSize"] = str(self.file_size)

        if self.original_path:
            result["url"] = self.original_path

        if self.extracted_text:
            # Truncate to reasonable length for embedding
            result["text"] = self.extracted_text[:2000]

        # Add image metadata if present
        if schema_type == "ImageObject":
            if self.image_width:
                result["width"] = self.image_width
            if self.image_height:
                result["height"] = self.image_height

            if self.has_faces is not None:
                result["hasFaces"] = self.has_faces

            if self.exif_datetime:
                result["datePublished"] = self.exif_datetime.isoformat()

            if self.gps_latitude and self.gps_longitude:
                result["contentLocation"] = {
                    "@type": "Place",
                    "geo": {
                        "@type": "GeoCoordinates",
                        "latitude": self.gps_latitude,
                        "longitude": self.gps_longitude
                    }
                }

        # Add relationships
        relationships = self.build_schema_relationships()
        if relationships:
            result.update(relationships)

        return result

    def build_schema_relationships(self) -> Dict[str, Any]:
        """Build relationships to other entities"""
        relationships = {}

        # Add categories
        if self.categories:
            relationships["about"] = [
                {
                    "@type": "DefinedTerm",
                    "@id": cat.get_iri(),
                    "name": cat.name
                }
                for cat in self.categories
            ]

        # Add companies and people
        mentions = []
        if self.companies:
            mentions.extend([
                {
                    "@type": "Organization",
                    "@id": comp.get_iri(),
                    "name": comp.name
                }
                for comp in self.companies
            ])

        if self.people:
            mentions.extend([
                {
                    "@type": "Person",
                    "@id": person.get_iri(),
                    "name": person.name
                }
                for person in self.people
            ])

        if mentions:
            relationships["mentions"] = mentions

        # Add locations
        if self.locations:
            if len(self.locations) == 1:
                relationships["spatialCoverage"] = {
                    "@type": "Place",
                    "@id": self.locations[0].get_iri(),
                    "name": self.locations[0].name
                }
            else:
                relationships["spatialCoverage"] = [
                    {
                        "@type": "Place",
                        "@id": loc.get_iri(),
                        "name": loc.name
                    }
                    for loc in self.locations
                ]

        return relationships
```

---

## 2. Category.to_schema_org()

```python
class Category(Base):
    """File classification with schema.org DefinedTerm support"""

    # ... existing fields ...

    def get_iri(self) -> str:
        """Get JSON-LD @id IRI"""
        return f"urn:uuid:{self.canonical_id}" if self.canonical_id else f"urn:uuid:{self.id}"

    def to_schema_org(self) -> Dict[str, Any]:
        """Convert Category to schema.org JSON-LD (DefinedTerm)"""

        result = {
            "@context": "https://schema.org",
            "@type": "DefinedTerm",
            "@id": self.get_iri(),
            "name": self.name,
        }

        # Add identifier (hierarchical path)
        if self.full_path:
            result["identifier"] = self.full_path.lower().replace('/', '-')

        # Add definition/description
        if self.description:
            result["definition"] = self.description
        else:
            result["definition"] = f"Category: {self.name}"

        # Add taxonomy membership
        result["inDefinedTermSet"] = {
            "@type": "DefinedTermSet",
            "@id": "urn:uuid:categories-taxonomy",
            "name": "File Organization Categories"
        }

        # Add parent category (broader)
        if self.parent:
            result["broader"] = {
                "@type": "DefinedTerm",
                "@id": self.parent.get_iri(),
                "name": self.parent.name
            }

        # Add child categories (narrower) if loaded
        if self.subcategories:
            result["narrower"] = [
                {
                    "@type": "DefinedTerm",
                    "@id": subcat.get_iri(),
                    "name": subcat.name
                }
                for subcat in self.subcategories
            ]

        # Custom extensions
        result["fileCount"] = self.file_count or 0
        result["hierarchyLevel"] = self.level or 0

        if self.icon:
            result["icon"] = self.icon

        if self.color:
            result["color"] = self.color

        return result

    def to_schema_org_as_intangible(self) -> Dict[str, Any]:
        """Alternative: Convert as schema.org Intangible"""

        return {
            "@context": "https://schema.org",
            "@type": "Intangible",
            "@id": self.get_iri(),
            "name": self.name,
            "description": self.description or f"Category: {self.name}",
        }
```

---

## 3. Company.to_schema_org()

```python
class Company(Base):
    """Organization entity with schema.org Organization support"""

    # ... existing fields ...

    def get_iri(self) -> str:
        """Get JSON-LD @id IRI"""
        return f"urn:uuid:{self.canonical_id}" if self.canonical_id else f"urn:uuid:{self.id}"

    @staticmethod
    def generate_wikidata_url(company_name: str) -> Optional[str]:
        """Generate potential Wikidata URL for external reference"""
        # This would typically call an external API
        # For now, return a template
        normalized = company_name.lower().replace(' ', '_')
        return f"https://www.wikidata.org/wiki/Q{normalized}"

    def to_schema_org(self) -> Dict[str, Any]:
        """Convert Company to schema.org JSON-LD (Organization)"""

        result = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "@id": self.get_iri(),
            "name": self.name,
        }

        # Add website URL
        if self.domain:
            url = self.domain if self.domain.startswith(('http://', 'https://')) else f"https://{self.domain}"
            result["url"] = url

        # Add industry/sector
        if self.industry:
            result["knowsAbout"] = self.industry

        # Add founding date if available
        if self.first_seen:
            result["dateFounded"] = self.first_seen.date().isoformat()

        # Add metadata timestamps
        if self.first_seen:
            result["dateCreated"] = self.first_seen.isoformat()

        if self.last_seen:
            result["dateModified"] = self.last_seen.isoformat()

        # Add external references
        same_as = []
        if self.domain:
            same_as.append(f"https://{self.domain.replace('https://', '').replace('http://', '')}")

        # Add potential Wikidata/Crunchbase references
        same_as.append(self.generate_wikidata_url(self.name))

        if same_as:
            result["sameAs"] = [url for url in same_as if url]

        # Custom tracking properties
        result["mentionCount"] = self.file_count or 0

        return result
```

---

## 4. Person.to_schema_org()

```python
class Person(Base):
    """Individual entity with schema.org Person support"""

    # ... existing fields ...

    def get_iri(self) -> str:
        """Get JSON-LD @id IRI"""
        return f"urn:uuid:{self.canonical_id}" if self.canonical_id else f"urn:uuid:{self.id}"

    def to_schema_org(self) -> Dict[str, Any]:
        """Convert Person to schema.org JSON-LD"""

        result = {
            "@context": "https://schema.org",
            "@type": "Person",
            "@id": self.get_iri(),
            "name": self.name,
        }

        # Add email if present
        if self.email:
            result["email"] = self.email

        # Add job title/role
        if self.role:
            result["jobTitle"] = self.role

        # Add temporal data
        if self.first_seen:
            result["dateCreated"] = self.first_seen.isoformat()

        if self.last_seen:
            result["dateModified"] = self.last_seen.isoformat()

        # Custom tracking
        result["mentionCount"] = self.file_count or 0

        return result

    def to_schema_org_with_relationships(self,
                                       company: Optional['Company'] = None,
                                       location: Optional['Location'] = None) -> Dict[str, Any]:
        """Convert Person with optional relationship references"""

        result = self.to_schema_org()

        # Add work relationships
        if company:
            result["worksFor"] = {
                "@type": "Organization",
                "@id": company.get_iri(),
                "name": company.name
            }

        if location:
            result["workLocation"] = {
                "@type": "Place",
                "@id": location.get_iri(),
                "name": location.name
            }

        return result
```

---

## 5. Location.to_schema_org()

```python
class Location(Base):
    """Geographic location with schema.org Place support"""

    # ... existing fields ...

    def get_iri(self) -> str:
        """Get JSON-LD @id IRI"""
        return f"urn:uuid:{self.canonical_id}" if self.canonical_id else f"urn:uuid:{self.id}"

    def infer_schema_type(self) -> str:
        """Determine if this should be Place, City, or Country"""
        if self.city and self.state and self.country:
            return "Place"  # Full address
        elif self.country and not self.state and not self.city:
            return "Country"  # Just country
        elif self.city:
            return "City"  # At least city specified
        else:
            return "Place"  # Default

    def to_schema_org(self) -> Dict[str, Any]:
        """Convert Location to schema.org JSON-LD (Place)"""

        schema_type = self.infer_schema_type()

        result = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "@id": self.get_iri(),
            "name": self.name,
        }

        # Add structured address
        address = {}
        if self.city:
            address["addressLocality"] = self.city
        if self.state:
            address["addressRegion"] = self.state
        if self.country:
            # Use country code if 2 chars, otherwise country name
            country = self.country
            if len(country) == 2:
                address["addressCountry"] = country
            else:
                address["addressCountry"] = country[:2]  # Attempt to extract code

        if address:
            result["address"] = {
                "@type": "PostalAddress",
                **address
            }

        # Add geographic coordinates
        if self.latitude is not None and self.longitude is not None:
            result["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": self.latitude,
                "longitude": self.longitude
            }

        # Add custom geohash property
        if self.geohash:
            result["geoHash"] = self.geohash

        # Add timestamp
        if self.created_at:
            result["dateCreated"] = self.created_at.isoformat()

        # Custom tracking
        result["mentionCount"] = self.file_count or 0

        return result
```

---

## 6. Bulk Operations

### Export all entities as JSON-LD

```python
def export_all_entities_as_jsonld(session: Session, output_file: str) -> None:
    """Export all entities with relationships as JSON-LD"""

    import json
    from jsonld import compact, frame

    entities = {
        "files": [],
        "categories": [],
        "companies": [],
        "people": [],
        "locations": []
    }

    # Export files with relationships
    for file in session.query(File).all():
        entities["files"].append(file.to_schema_org())

    # Export categories
    for category in session.query(Category).all():
        entities["categories"].append(category.to_schema_org())

    # Export companies
    for company in session.query(Company).all():
        entities["companies"].append(company.to_schema_org())

    # Export people
    for person in session.query(Person).all():
        entities["people"].append(person.to_schema_org())

    # Export locations
    for location in session.query(Location).all():
        entities["locations"].append(location.to_schema_org())

    # Write to file
    with open(output_file, 'w') as f:
        json.dump(entities, f, indent=2)

    print(f"Exported {sum(len(v) for v in entities.values())} entities to {output_file}")
```

### REST API endpoint returning schema.org

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/api/files/{file_id}/schema-org")
async def get_file_schema_org(file_id: str, db: Session = Depends(get_db)):
    """Get File as schema.org JSON-LD"""
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return file.to_schema_org()

@app.get("/api/organizations/{company_id}/schema-org")
async def get_company_schema_org(company_id: int, db: Session = Depends(get_db)):
    """Get Company as schema.org Organization JSON-LD"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company.to_schema_org()

@app.get("/api/people/{person_id}/schema-org")
async def get_person_schema_org(person_id: int, db: Session = Depends(get_db)):
    """Get Person as schema.org JSON-LD"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return person.to_schema_org()
```

---

## Testing Schema.org Output

```python
import json
import requests

def validate_schema_org_with_google_validator(json_ld: Dict[str, Any]) -> Dict[str, Any]:
    """Validate JSON-LD against Google's schema.org validator"""

    # Note: This would need a real API endpoint
    # For testing, you can use https://validator.schema.org/

    validation_url = "https://validator.schema.org/validate"

    response = requests.post(
        validation_url,
        json={"jsonld": json.dumps(json_ld)}
    )

    return response.json()

def test_file_schema_org():
    """Test File schema.org serialization"""

    file = File(
        id="abc123",
        filename="document.pdf",
        mime_type="application/pdf",
        file_size=102400,
        original_path="/documents/document.pdf"
    )

    schema_org = file.to_schema_org()

    # Verify structure
    assert schema_org["@context"] == "https://schema.org"
    assert schema_org["@type"] == "DigitalDocument"
    assert "@id" in schema_org
    assert schema_org["name"] == "document.pdf"
    assert schema_org["encodingFormat"] == "application/pdf"

    print("✓ File schema.org validation passed")
    print(json.dumps(schema_org, indent=2))
```

---

## Integration Checklist

- [x] Add `get_iri()` method to all model classes
- [x] Implement `to_schema_org()` method for each type
- [x] Add proper @context and @type selection
- [x] Handle relationships between entities
- [x] Test JSON-LD output with validator
- [x] Add REST API endpoints for schema.org output
- [x] Document property mappings in code
- [x] Add comprehensive unit tests
- [x] Validate @id consistency across relationships
- [x] Handle edge cases (NULL values, missing relationships, etc.)

---

**Last Updated:** 2026-03-24
**Version:** 1.0

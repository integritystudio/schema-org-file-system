"""
Base classes and mixins for schema.org JSON-LD serialization.

Eliminates boilerplate from individual model implementations by:
- Centralizing @context constant
- Providing get_iri() strategy
- Common property setters
- Template for to_schema_org() pattern
"""

from typing import Any, Dict, Optional


class IriMixin:
  """Mixin for consistent IRI generation patterns."""

  @staticmethod
  def _iri_from_uuid(uuid_value: Optional[str]) -> Optional[str]:
    """Generate urn:uuid: IRI from UUID string."""
    if not uuid_value:
      return None
    return f"urn:uuid:{uuid_value}"

  @staticmethod
  def _iri_from_sha256(hash_value: str) -> str:
    """Generate urn:sha256: IRI from hash string."""
    return f"urn:sha256:{hash_value}"


class PropertyBuilder:
  """Utility for building schema.org properties in a standardized way."""

  @staticmethod
  def add_if_present(obj: Dict[str, Any], key: str, value: Any) -> None:
    """Add property to dict only if value is not None."""
    if value is not None:
      obj[key] = value

  @staticmethod
  def add_iso_datetime(obj: Dict[str, Any], key: str, dt: Optional[Any]) -> None:
    """Add ISO-formatted datetime if present."""
    if dt is not None:
      obj[key] = dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)

  @staticmethod
  def add_string_if_present(obj: Dict[str, Any], key: str, value: Optional[str]) -> None:
    """Add string property if present and non-empty."""
    if value and isinstance(value, str):
      obj[key] = value

  @staticmethod
  def add_numeric_if_present(obj: Dict[str, Any], key: str, value: Optional[Any]) -> None:
    """Add numeric property if present and non-zero."""
    if value is not None and (not isinstance(value, (int, float)) or value != 0):
      obj[key] = value


class EntityReferenceBuilder:
  """Builder for schema.org entity references (Person, Organization, Place, etc.)."""

  @staticmethod
  def build_person_reference(person_id: str, person_name: str) -> Dict[str, Any]:
    """Build a Person entity reference."""
    return {
      "@type": "Person",
      "@id": person_id,
      "name": person_name,
    }

  @staticmethod
  def build_organization_reference(org_id: str, org_name: str) -> Dict[str, Any]:
    """Build an Organization entity reference."""
    return {
      "@type": "Organization",
      "@id": org_id,
      "name": org_name,
    }

  @staticmethod
  def build_place_reference(place_id: str, place_name: str) -> Dict[str, Any]:
    """Build a Place entity reference."""
    return {
      "@type": "Place",
      "@id": place_id,
      "name": place_name,
    }

  @staticmethod
  def build_defined_term_reference(term_id: str, term_name: str) -> Dict[str, Any]:
    """Build a DefinedTerm entity reference (for categories)."""
    return {
      "@type": "DefinedTerm",
      "@id": term_id,
      "name": term_name,
    }


class RelationshipBuilder:
  """Builder for schema.org relationships between entities."""

  @staticmethod
  def build_geo_coordinates(latitude: float, longitude: float) -> Dict[str, Any]:
    """Build a GeoCoordinates object."""
    return {
      "@type": "GeoCoordinates",
      "latitude": latitude,
      "longitude": longitude,
    }

  @staticmethod
  def build_postal_address(
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
  ) -> Optional[Dict[str, Any]]:
    """Build a PostalAddress object."""
    address = {}

    if city:
      address["addressLocality"] = city
    if state:
      address["addressRegion"] = state
    if country:
      address["addressCountry"] = country

    if not address:
      return None

    return {
      "@type": "PostalAddress",
      **address,
    }

  @staticmethod
  def build_mentions_list(
    companies: Optional[list] = None,
    people: Optional[list] = None,
  ) -> Optional[list]:
    """Build mentions array from related entities."""
    mentions = []

    if companies:
      for company in companies:
        mentions.append(
          EntityReferenceBuilder.build_organization_reference(
            company.get_iri(),
            company.name,
          )
        )

    if people:
      for person in people:
        mentions.append(
          EntityReferenceBuilder.build_person_reference(
            person.get_iri(),
            person.name,
          )
        )

    return mentions if mentions else None

  @staticmethod
  def build_spatial_coverage(locations: Optional[list]) -> Optional[Any]:
    """Build spatialCoverage property from locations."""
    if not locations:
      return None

    if len(locations) == 1:
      loc = locations[0]
      return EntityReferenceBuilder.build_place_reference(loc.get_iri(), loc.name)

    return [
      EntityReferenceBuilder.build_place_reference(loc.get_iri(), loc.name)
      for loc in locations
    ]

"""
Base classes and mixins for schema.org JSON-LD serialization.

Eliminates boilerplate from individual model implementations by:
- Centralizing @context constant
- Providing get_iri() strategy
- Common property setters
- Template for to_schema_org() pattern
"""

from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


# Standard schema.org context with custom namespace declarations
# Supports both standard schema.org properties and custom extensions (e.g., ml:hasFaces)
SCHEMA_ORG_CONTEXT = {
  "@vocab": "https://schema.org/",
  "ml": "https://example.org/ml-properties/"
}


class SchemaOrgSerializable(ABC):
  """
  Abstract base class for entities that serialize to schema.org JSON-LD.

  Subclasses must implement:
  - get_iri() → str: Return @id for this entity
  - get_schema_type() → str: Return @type (e.g., "Person", "Organization")
  """

  @abstractmethod
  def get_iri(self) -> str:
    """Get the JSON-LD @id IRI for this entity."""
    pass

  @abstractmethod
  def get_schema_type(self) -> str:
    """Get the @type (schema.org type name) for this entity."""
    pass

  def to_schema_org(self) -> Dict[str, Any]:
    """
    Base schema.org JSON-LD structure. Override in subclasses to add properties.

    Returns minimal valid JSON-LD document with @context, @id, @type.
    """
    return {
      "@context": SCHEMA_ORG_CONTEXT,
      "@type": self.get_schema_type(),
      "@id": self.get_iri(),
    }


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

"""
Base classes and mixins for schema.org JSON-LD serialization.

Provides IRI generation utilities for consistent identifier patterns.
Builder functions are centralized in schema_org_builders.py.
"""

from typing import Optional


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

"""Mixin for schema.org JSON-LD serialization.

Cannot use abc.ABC here — SQLAlchemy's DeclarativeMeta conflicts with ABCMeta.
Use NotImplementedError to enforce the interface at runtime instead.
"""

from typing import Dict, Any


class SchemaOrgSerializable:
    """Mixin requiring schema.org JSON-LD serialization methods.

    Classes that inherit this alongside SQLAlchemy's Base must implement:
      - get_iri() -> str
      - get_schema_type() -> str
      - to_schema_org() -> Dict[str, Any]
    """

    def get_iri(self) -> str:
        """Return the JSON-LD @id IRI for this entity."""
        raise NotImplementedError(f"{type(self).__name__} must implement get_iri()")

    def get_schema_type(self) -> str:
        """Return the schema.org @type string for this entity."""
        raise NotImplementedError(f"{type(self).__name__} must implement get_schema_type()")

    def to_schema_org(self) -> Dict[str, Any]:
        """Return a schema.org JSON-LD representation of this entity."""
        raise NotImplementedError(f"{type(self).__name__} must implement to_schema_org()")

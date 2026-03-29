"""
Unified service for exporting entities to schema.org JSON-LD in various formats.

Supports three output formats:
  - json   : JSON array, pretty-printed by default
  - ndjson : Newline-delimited JSON (one entity per line, streaming-friendly)
  - graph  : JSON-LD @graph structure (recommended for multiple entity types)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Type, Union

from sqlalchemy.orm import Session

from .schema_org_base import SchemaOrgSerializable

SCHEMA_ORG_CONTEXT = "https://schema.org"

# Sentinel used in export_with_graph to populate all known entity classes
_SENTINEL_ALL = object()


class SchemaOrgExporter:
    """Export schema.org JSON-LD for one or more entity types.

    Usage::

        exporter = SchemaOrgExporter(session)
        exporter.export_to_file("out.json", entity_classes=[File, Category])
        exporter.export_to_ndjson("out.ndjson", entity_classes=[File])
        exporter.export_with_graph("out-graph.json")
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def export_to_file(
        self,
        output_path: Union[str, Path],
        entity_classes: Optional[List[Type[SchemaOrgSerializable]]] = None,
        pretty: bool = True,
    ) -> int:
        """Export entities to a JSON file (array of JSON-LD objects).

        Args:
            output_path: Destination file path.
            entity_classes: List of SQLAlchemy model classes to export.
                Defaults to all registered entity types when None.
            pretty: Whether to pretty-print (indent=2).

        Returns:
            Total number of entities written.
        """
        records = self._collect_records(entity_classes)
        indent = 2 if pretty else None
        Path(output_path).write_text(json.dumps(records, indent=indent), encoding="utf-8")
        return len(records)

    def export_to_ndjson(
        self,
        output_path: Union[str, Path],
        entity_classes: Optional[List[Type[SchemaOrgSerializable]]] = None,
    ) -> int:
        """Export entities to a newline-delimited JSON file.

        Each entity is serialized to a single line. Suitable for streaming
        and large-scale processing.

        Args:
            output_path: Destination file path.
            entity_classes: List of SQLAlchemy model classes to export.

        Returns:
            Total number of entities written.
        """
        records = self._collect_records(entity_classes)
        lines = [json.dumps(r, separators=(",", ":")) for r in records]
        Path(output_path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return len(records)

    def export_with_graph(
        self,
        output_path: Union[str, Path],
        entity_classes: Optional[List[Type[SchemaOrgSerializable]]] = None,
        pretty: bool = True,
    ) -> int:
        """Export entities as a JSON-LD @graph document.

        The output structure is::

            {
                "@context": "https://schema.org",
                "@graph": [ ... ]
            }

        Each entity in @graph omits its own @context (it is hoisted to the
        document root).

        Args:
            output_path: Destination file path.
            entity_classes: List of SQLAlchemy model classes to export.
            pretty: Whether to pretty-print (indent=2).

        Returns:
            Total number of entities written.
        """
        records = self._collect_records(entity_classes)
        # Hoist @context to document level; strip per-entity copies
        graph_nodes = []
        for rec in records:
            node = {k: v for k, v in rec.items() if k != "@context"}
            graph_nodes.append(node)

        document: Dict[str, Any] = {
            "@context": SCHEMA_ORG_CONTEXT,
            "@graph": graph_nodes,
        }
        indent = 2 if pretty else None
        Path(output_path).write_text(json.dumps(document, indent=indent), encoding="utf-8")
        return len(records)

    def get_graph_document(
        self,
        entity_classes: Optional[List[Type[SchemaOrgSerializable]]] = None,
    ) -> Dict[str, Any]:
        """Return a JSON-LD @graph document as a Python dict (no I/O).

        Useful for in-memory use, REST API responses, etc.

        Args:
            entity_classes: List of SQLAlchemy model classes to export.

        Returns:
            Dict with "@context" and "@graph" keys.
        """
        records = self._collect_records(entity_classes)
        graph_nodes = [{k: v for k, v in rec.items() if k != "@context"} for rec in records]
        return {
            "@context": SCHEMA_ORG_CONTEXT,
            "@graph": graph_nodes,
        }

    # ------------------------------------------------------------------
    # Filtering helpers
    # ------------------------------------------------------------------

    def export_entities_filtered(
        self,
        output_path: Union[str, Path],
        entity_class: Type[SchemaOrgSerializable],
        entity_ids: Sequence[Any],
        pretty: bool = True,
    ) -> int:
        """Export a filtered subset of entities by primary key.

        Args:
            output_path: Destination file path.
            entity_class: SQLAlchemy model class to query.
            entity_ids: Primary key values to include.
            pretty: Whether to pretty-print.

        Returns:
            Number of entities written.
        """
        pk_col = entity_class.__mapper__.primary_key[0]
        rows = self._session.query(entity_class).filter(pk_col.in_(entity_ids)).all()
        records = [r.to_schema_org() for r in rows]
        indent = 2 if pretty else None
        Path(output_path).write_text(json.dumps(records, indent=indent), encoding="utf-8")
        return len(records)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _collect_records(
        self,
        entity_classes: Optional[List[Type[SchemaOrgSerializable]]],
    ) -> List[Dict[str, Any]]:
        """Query all instances of each entity class and call to_schema_org().

        Args:
            entity_classes: Classes to query; None queries default entity types.

        Returns:
            Flat list of JSON-LD dicts.
        """
        if entity_classes is None:
            entity_classes = self._default_entity_classes()

        records: List[Dict[str, Any]] = []
        for cls in entity_classes:
            rows = self._session.query(cls).all()
            for row in rows:
                records.append(row.to_schema_org())
        return records

    @staticmethod
    def _default_entity_classes() -> List[Type[SchemaOrgSerializable]]:
        """Return the canonical set of entity classes for full exports."""
        # Import here to avoid circular imports at module load time
        from .models import File, Category, Company, Person, Location
        return [File, Category, Company, Person, Location]

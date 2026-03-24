"""
Schema.org exporter service for bulk entity serialization.

Consolidates export patterns and supports multiple output formats.
"""

import json
from typing import Any, Dict, List, Optional, Type
from pathlib import Path

from sqlalchemy.orm import Session


class SchemaOrgExporter:
  """
  Export entities from the database to schema.org JSON-LD format.

  Supports multiple output formats and automatic relationship handling.
  """

  def __init__(self, session: Session):
    """
    Initialize exporter with database session.

    Args:
      session: SQLAlchemy Session for database queries
    """
    self.session = session

  def export_entity_type(
    self,
    entity_class: Type,
    output_format: str = "json-ld",
  ) -> List[Dict[str, Any]]:
    """
    Export all instances of an entity type.

    Args:
      entity_class: Model class to export (File, Category, Company, etc.)
      output_format: Output format ('json-ld' or 'dict')

    Returns:
      List of exported entities with schema.org serialization
    """
    entities = []
    for entity in self.session.query(entity_class).all():
      if hasattr(entity, 'to_schema_org'):
        entities.append(entity.to_schema_org())
      elif hasattr(entity, 'to_dict'):
        entities.append(entity.to_dict())
      else:
        # Fallback: return entity as-is (likely breaks schema.org compliance)
        entities.append({'id': getattr(entity, 'id', None)})

    return entities

  def export_all_entities(
    self,
    entity_classes: Optional[List[Type]] = None,
    output_format: str = "json-ld",
  ) -> Dict[str, List[Dict[str, Any]]]:
    """
    Export multiple entity types.

    Args:
      entity_classes: List of model classes to export. If None, exports all.
      output_format: Output format ('json-ld' or 'dict')

    Returns:
      Dict mapping entity type names to lists of exported entities
    """
    result = {}

    if entity_classes is None:
      # Import here to avoid circular dependency
      from .models import File, Category, Company, Person, Location
      entity_classes = [File, Category, Company, Person, Location]

    for entity_class in entity_classes:
      entity_name = entity_class.__name__.lower()
      result[f"{entity_name}s"] = self.export_entity_type(entity_class, output_format)

    return result

  def export_to_file(
    self,
    output_path: str,
    entity_classes: Optional[List[Type]] = None,
    output_format: str = "json-ld",
    pretty: bool = True,
  ) -> None:
    """
    Export entities to a JSON file.

    Args:
      output_path: Path to output file
      entity_classes: List of model classes to export
      output_format: Output format ('json-ld' or 'dict')
      pretty: Whether to pretty-print JSON
    """
    entities = self.export_all_entities(entity_classes, output_format)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
      if pretty:
        json.dump(entities, f, indent=2, ensure_ascii=False)
      else:
        json.dump(entities, f, ensure_ascii=False)

    entity_count = sum(len(v) for v in entities.values())
    print(f"✓ Exported {entity_count} entities to {output_path}")

  def export_to_ndjson(
    self,
    output_path: str,
    entity_classes: Optional[List[Type]] = None,
    output_format: str = "json-ld",
  ) -> None:
    """
    Export entities to NDJSON format (one JSON object per line).

    Useful for streaming and incremental processing.

    Args:
      output_path: Path to output file
      entity_classes: List of model classes to export
      output_format: Output format ('json-ld' or 'dict')
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    entity_count = 0

    with open(output_path, 'w', encoding='utf-8') as f:
      if entity_classes is None:
        from .models import File, Category, Company, Person, Location
        entity_classes = [File, Category, Company, Person, Location]

      for entity_class in entity_classes:
        for entity in self.session.query(entity_class).all():
          if hasattr(entity, 'to_schema_org'):
            entity_data = entity.to_schema_org()
          elif hasattr(entity, 'to_dict'):
            entity_data = entity.to_dict()
          else:
            entity_data = {'id': getattr(entity, 'id', None)}

          f.write(json.dumps(entity_data, ensure_ascii=False) + '\n')
          entity_count += 1

    print(f"✓ Exported {entity_count} entities to {output_path}")

  def export_with_graph(
    self,
    output_path: str,
    entity_classes: Optional[List[Type]] = None,
  ) -> None:
    """
    Export entities as a JSON-LD @graph structure.

    This groups all entities into a single @graph array, which is the
    recommended format for representing multiple interconnected entities.

    Args:
      output_path: Path to output file
      entity_classes: List of model classes to export
    """
    if entity_classes is None:
      from .models import File, Category, Company, Person, Location
      entity_classes = [File, Category, Company, Person, Location]

    all_entities = []
    for entity_class in entity_classes:
      for entity in self.session.query(entity_class).all():
        if hasattr(entity, 'to_schema_org'):
          all_entities.append(entity.to_schema_org())
        elif hasattr(entity, 'to_dict'):
          all_entities.append(entity.to_dict())

    output_data = {
      "@context": "https://schema.org",
      "@graph": all_entities,
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
      json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Exported {len(all_entities)} entities in @graph format to {output_path}")


def export_all_entities_as_jsonld(
  session: Session,
  output_file: str,
) -> None:
  """
  Convenience function matching the IMPLEMENTATION_EXAMPLES.md signature.

  Args:
    session: Database session
    output_file: Output file path
  """
  exporter = SchemaOrgExporter(session)
  exporter.export_to_file(output_file)

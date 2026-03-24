"""
Alternative schema.org representations for entities.

Some entities can be represented in multiple ways depending on context.
This module provides factory functions for generating these variants.
"""

from typing import Any, Dict, Optional
from datetime import datetime


class CategoryVariants:
  """
  Alternative representations for Category entity.

  Categories can be represented as:
  1. DefinedTerm (primary) - for taxonomy/vocabulary context
  2. Intangible - simplified representation
  3. Thing with broadMatch/narrowMatch - for linked data
  """

  @staticmethod
  def to_defined_term(
    canonical_id: Optional[str],
    name: str,
    description: Optional[str],
    full_path: Optional[str],
    parent_iri: Optional[str] = None,
    children_iris: Optional[Dict[str, str]] = None,
    file_count: int = 0,
    icon: Optional[str] = None,
    color: Optional[str] = None,
  ) -> Dict[str, Any]:
    """
    Represent Category as a DefinedTerm (recommended).

    DefinedTerm is the proper schema.org type for categories, terms,
    and items in a controlled vocabulary.

    Args:
      canonical_id: UUID for @id
      name: Category name
      description: Category description
      full_path: Hierarchical path (e.g., "Legal/Contracts")
      parent_iri: @id of parent category (if any)
      children_iris: Dict of child @ids to names
      file_count: Number of files in category
      icon: Emoji or icon identifier
      color: Hex color code

    Returns:
      JSON-LD object as DefinedTerm
    """
    result = {
      "@context": "https://schema.org",
      "@type": "DefinedTerm",
      "@id": f"urn:uuid:{canonical_id}" if canonical_id else None,
      "name": name,
    }

    # Remove None @id
    if result["@id"] is None:
      del result["@id"]

    # Add identifier (hierarchical path)
    if full_path:
      result["identifier"] = full_path.lower().replace('/', '-')

    # Add definition
    if description:
      result["definition"] = description
    else:
      result["definition"] = f"Category: {name}"

    # Add taxonomy membership
    result["inDefinedTermSet"] = {
      "@type": "DefinedTermSet",
      "@id": "urn:uuid:categories-taxonomy",
      "name": "File Organization Categories",
    }

    # Add parent (broader term)
    if parent_iri:
      result["broader"] = {
        "@type": "DefinedTerm",
        "@id": parent_iri,
      }

    # Add children (narrower terms)
    if children_iris:
      result["narrower"] = [
        {
          "@type": "DefinedTerm",
          "@id": child_id,
          "name": child_name,
        }
        for child_id, child_name in children_iris.items()
      ]

    # Custom extensions
    result["fileCount"] = file_count
    result["hierarchyLevel"] = len(full_path.split('/')) - 1 if full_path else 0

    if icon:
      result["icon"] = icon

    if color:
      result["color"] = color

    return result

  @staticmethod
  def to_intangible(
    canonical_id: Optional[str],
    name: str,
    description: Optional[str],
  ) -> Dict[str, Any]:
    """
    Simplified representation as Intangible.

    Use when a simpler, more generic representation is needed
    (e.g., for external systems that don't understand DefinedTerm).

    Args:
      canonical_id: UUID for @id
      name: Category name
      description: Category description

    Returns:
      JSON-LD object as Intangible
    """
    return {
      "@context": "https://schema.org",
      "@type": "Intangible",
      "@id": f"urn:uuid:{canonical_id}" if canonical_id else None,
      "name": name,
      "description": description or f"Category: {name}",
    }


class PersonVariants:
  """Alternative representations for Person entity."""

  @staticmethod
  def to_person_with_context(
    canonical_id: str,
    name: str,
    email: Optional[str] = None,
    role: Optional[str] = None,
    company_iri: Optional[str] = None,
    company_name: Optional[str] = None,
    location_iri: Optional[str] = None,
    location_name: Optional[str] = None,
    file_count: int = 0,
    first_seen: Optional[datetime] = None,
    last_seen: Optional[datetime] = None,
  ) -> Dict[str, Any]:
    """
    Represent Person with work relationships and context.

    Includes employment (worksFor) and location (workLocation) relationships.

    Args:
      canonical_id: UUID for @id
      name: Person name
      email: Email address
      role: Job title/role
      company_iri: Organization @id
      company_name: Organization name
      location_iri: Place @id
      location_name: Place name
      file_count: Mention count
      first_seen: First detection timestamp
      last_seen: Last detection timestamp

    Returns:
      JSON-LD object as Person with context
    """
    result = {
      "@context": "https://schema.org",
      "@type": "Person",
      "@id": f"urn:uuid:{canonical_id}",
      "name": name,
    }

    if email:
      result["email"] = email

    if role:
      result["jobTitle"] = role

    if first_seen:
      result["dateCreated"] = first_seen.isoformat()

    if last_seen:
      result["dateModified"] = last_seen.isoformat()

    result["mentionCount"] = file_count

    # Add employment relationship
    if company_iri and company_name:
      result["worksFor"] = {
        "@type": "Organization",
        "@id": company_iri,
        "name": company_name,
      }

    # Add location relationship
    if location_iri and location_name:
      result["workLocation"] = {
        "@type": "Place",
        "@id": location_iri,
        "name": location_name,
      }

    return result


class FileVariants:
  """Alternative representations for File entity."""

  @staticmethod
  def to_creative_work(
    canonical_id: str,
    name: str,
    mime_type: Optional[str] = None,
    author_name: Optional[str] = None,
    author_iri: Optional[str] = None,
    created_at: Optional[datetime] = None,
    modified_at: Optional[datetime] = None,
  ) -> Dict[str, Any]:
    """
    Represent File as a CreativeWork.

    Use for files that are primarily creative/intellectual output
    (documents, articles, scripts, etc.).

    Args:
      canonical_id: SHA256 for @id
      name: File name
      mime_type: MIME type
      author_name: Author name
      author_iri: Author @id
      created_at: Creation timestamp
      modified_at: Modification timestamp

    Returns:
      JSON-LD object as CreativeWork
    """
    result = {
      "@context": "https://schema.org",
      "@type": "CreativeWork",
      "@id": f"urn:sha256:{canonical_id}",
      "name": name,
    }

    if mime_type:
      result["encodingFormat"] = mime_type

    if author_iri and author_name:
      result["author"] = {
        "@type": "Person",
        "@id": author_iri,
        "name": author_name,
      }

    if created_at:
      result["dateCreated"] = created_at.isoformat()

    if modified_at:
      result["dateModified"] = modified_at.isoformat()

    return result

  @staticmethod
  def to_media_object(
    canonical_id: str,
    name: str,
    mime_type: str,
    schema_type: str,  # ImageObject, VideoObject, AudioObject
    url: Optional[str] = None,
    duration: Optional[str] = None,
  ) -> Dict[str, Any]:
    """
    Represent File as a MediaObject variant.

    Use for media files (images, videos, audio).

    Args:
      canonical_id: SHA256 for @id
      name: File name
      mime_type: MIME type
      schema_type: Specific schema.org media type
      url: Accessible URL if available
      duration: Duration (for video/audio)

    Returns:
      JSON-LD object as media type
    """
    result = {
      "@context": "https://schema.org",
      "@type": schema_type,
      "@id": f"urn:sha256:{canonical_id}",
      "name": name,
      "encodingFormat": mime_type,
    }

    if url:
      result["url"] = url

    if duration:
      result["duration"] = duration

    return result

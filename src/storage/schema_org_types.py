#!/usr/bin/env python3
"""
Pydantic models for schema.org entity and property types.

Defines structured types for entity references, addresses, locations,
image metadata, and relationships used in schema.org serialization.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Entity Reference Types
# ============================================================================

class EntityReferenceBase(BaseModel):
  """Base entity reference with @type, @id, name."""
  type: str = Field(alias="@type")
  id: str = Field(alias="@id")
  name: str

  class Config:
    populate_by_name = True


class PersonReference(EntityReferenceBase):
  """Person entity reference."""
  type: str = Field("Person", alias="@type")

  class Config:
    populate_by_name = True


class OrganizationReference(EntityReferenceBase):
  """Organization entity reference."""
  type: str = Field("Organization", alias="@type")

  class Config:
    populate_by_name = True


class PlaceReference(EntityReferenceBase):
  """Place entity reference."""
  type: str = Field("Place", alias="@type")

  class Config:
    populate_by_name = True


class DefinedTermReference(EntityReferenceBase):
  """DefinedTerm entity reference."""
  type: str = Field("DefinedTerm", alias="@type")

  class Config:
    populate_by_name = True


# ============================================================================
# Address and Location Types
# ============================================================================

class PostalAddress(BaseModel):
  """PostalAddress with address components."""
  type: str = Field("PostalAddress", alias="@type")
  address_locality: Optional[str] = Field(None, alias="addressLocality")
  address_region: Optional[str] = Field(None, alias="addressRegion")
  address_country: Optional[str] = Field(None, alias="addressCountry")

  class Config:
    populate_by_name = True


class GeoCoordinates(BaseModel):
  """GeoCoordinates with latitude/longitude."""
  type: str = Field("GeoCoordinates", alias="@type")
  latitude: float
  longitude: float

  class Config:
    populate_by_name = True


class LocationObject(BaseModel):
  """Complete Place object with address and coordinates."""
  type: str = Field("Place", alias="@type")
  id: str = Field(alias="@id")
  name: str
  address: Optional[PostalAddress] = None
  geo: Optional[GeoCoordinates] = None

  class Config:
    populate_by_name = True


# ============================================================================
# Image Metadata Types
# ============================================================================

class ImageMetadata(BaseModel):
  """Image-specific metadata."""
  width: Optional[int] = None
  height: Optional[int] = None
  has_faces: Optional[bool] = Field(None, alias="hasFaces")
  content_location: Optional[Dict[str, Any]] = Field(None, alias="contentLocation")

  class Config:
    populate_by_name = True


# ============================================================================
# Relationship Types
# ============================================================================

class MentionItem(BaseModel):
  """Single mention in mentions list."""
  type: str = Field(alias="@type")
  id: str = Field(alias="@id")
  name: str

  class Config:
    populate_by_name = True


class MentionsList(BaseModel):
  """List of entity mentions."""
  items: List[MentionItem]


class SpatialCoverageItem(BaseModel):
  """Single spatial coverage item."""
  type: str = Field("Place", alias="@type")
  id: str = Field(alias="@id")
  name: str

  class Config:
    populate_by_name = True


class SpatialCoverageSingle(BaseModel):
  """Single location spatial coverage."""
  type: str = Field("Place", alias="@type")
  id: str = Field(alias="@id")
  name: str


class SpatialCoverageMultiple(BaseModel):
  """Multiple locations spatial coverage."""
  items: List[SpatialCoverageSingle]


# ============================================================================
# Property Builder Result Types
# ============================================================================

class PropertyValue(BaseModel):
  """Generic property value (for any type)."""
  key: str
  value: Any


class DateTimeIsoString(BaseModel):
  """ISO 8601 formatted datetime."""
  value: str = Field(description="ISO 8601 datetime string")


# ============================================================================
# Country Code Types
# ============================================================================

class CountryCode(BaseModel):
  """ISO 3166-1 alpha-2 country code."""
  code: str = Field(min_length=2, max_length=2, description="2-letter country code")
  name: Optional[str] = Field(None, description="Country name")


class CountryMapping(BaseModel):
  """Country name/input to ISO code mapping."""
  input: str = Field(description="User-provided country name, code, or alias")
  normalized_code: str = Field(description="Normalized ISO 3166-1 alpha-2 code")



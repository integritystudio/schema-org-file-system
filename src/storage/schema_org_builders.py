"""
Factory functions for building common schema.org structures.

Centralizes the pattern of building entity references and complex properties
that are repeated in multiple to_schema_org() implementations.
"""

from typing import Any, Dict, List, Optional


# ISO 3166-1 alpha-2 country codes mapping (country name/code → ISO code)
_COUNTRY_CODE_MAPPING = {
  # United States and territories
  'united states': 'US', 'usa': 'US', 'u.s.a': 'US',
  'us': 'US', 'america': 'US',
  # Common countries
  'france': 'FR', 'germany': 'DE', 'united kingdom': 'GB',
  'uk': 'GB', 'canada': 'CA', 'australia': 'AU',
  'japan': 'JP', 'china': 'CN', 'india': 'IN',
  'mexico': 'MX', 'brazil': 'BR', 'spain': 'ES',
  'italy': 'IT', 'netherlands': 'NL', 'belgium': 'BE',
  'switzerland': 'CH', 'sweden': 'SE', 'norway': 'NO',
  'denmark': 'DK', 'poland': 'PL', 'portugal': 'PT',
  'greece': 'GR', 'ireland': 'IE', 'singapore': 'SG',
  'south korea': 'KR', 'korea': 'KR', 'russia': 'RU',
  'south africa': 'ZA', 'new zealand': 'NZ', 'argentina': 'AR',
}


def _normalize_country_code(country: str) -> str:
  """
  Normalize country input to ISO 3166-1 alpha-2 code.

  Args:
    country: Country name, code, or alias

  Returns:
    ISO 3166-1 alpha-2 code (uppercase, 2 chars)

  Raises:
    ValueError: If country cannot be normalized to a valid code
  """
  if not country:
    raise ValueError("Country cannot be empty")

  country_lower = country.lower().strip()

  # If already a 2-char code, assume it's ISO and uppercase it
  if len(country_lower) == 2:
    return country_lower.upper()

  # Try to look up in mapping
  if country_lower in _COUNTRY_CODE_MAPPING:
    return _COUNTRY_CODE_MAPPING[country_lower]

  # Try to match as prefix (e.g., "fra" → "france" → "FR")
  for key, code in _COUNTRY_CODE_MAPPING.items():
    if key.startswith(country_lower) or country_lower.startswith(key[:3]):
      return code

  # Could not normalize
  raise ValueError(
    f"Cannot normalize country '{country}' to ISO code. "
    f"Provide 2-char ISO code or country name (e.g., 'US', 'France')"
  )


def build_entity_reference(
  entity_id: str,
  entity_type: str,
  entity_name: str,
) -> Dict[str, Any]:
  """
  Build a standard schema.org entity reference.

  Used for embedding related entities (Person, Organization, Place, etc.)
  as sub-objects with @id, @type, and name.

  Args:
    entity_id: IRI (@id value)
    entity_type: Schema.org type (e.g., "Person", "Organization")
    entity_name: Human-readable name

  Returns:
    Dict with @id, @type, and name
  """
  return {
    "@type": entity_type,
    "@id": entity_id,
    "name": entity_name,
  }


def build_location_reference(
  location_id: str,
  location_name: str,
) -> Dict[str, Any]:
  """Build a Place entity reference."""
  return build_entity_reference(location_id, "Place", location_name)


def build_organization_reference(
  company_id: str,
  company_name: str,
) -> Dict[str, Any]:
  """Build an Organization entity reference."""
  return build_entity_reference(company_id, "Organization", company_name)


def build_person_reference(
  person_id: str,
  person_name: str,
) -> Dict[str, Any]:
  """Build a Person entity reference."""
  return build_entity_reference(person_id, "Person", person_name)


def build_defined_term_reference(
  term_id: str,
  term_name: str,
) -> Dict[str, Any]:
  """Build a DefinedTerm entity reference (for categories)."""
  return build_entity_reference(term_id, "DefinedTerm", term_name)


def build_geo_coordinates(
  latitude: float,
  longitude: float,
) -> Dict[str, Any]:
  """
  Build a GeoCoordinates object.

  Args:
    latitude: Latitude value
    longitude: Longitude value

  Returns:
    Dict with @type, latitude, and longitude
  """
  return {
    "@type": "GeoCoordinates",
    "latitude": latitude,
    "longitude": longitude,
  }


def build_postal_address(
  city: Optional[str] = None,
  state: Optional[str] = None,
  country: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
  """
  Build a PostalAddress object.

  Args:
    city: City/locality
    state: State/region
    country: ISO 3166-1 alpha-2 code (e.g., 'US') or country name (e.g., 'France')

  Returns:
    Dict with @type and address components, or None if all inputs are None

  Raises:
    ValueError: If country is provided but cannot be normalized to ISO code
  """
  address = {}

  if city:
    address["addressLocality"] = city
  if state:
    address["addressRegion"] = state
  if country:
    # Normalize country to ISO 3166-1 alpha-2 code
    address["addressCountry"] = _normalize_country_code(country)

  if not address:
    return None

  return {
    "@type": "PostalAddress",
    **address,
  }


def build_location_object(
  location_id: str,
  location_name: str,
  latitude: Optional[float] = None,
  longitude: Optional[float] = None,
  city: Optional[str] = None,
  state: Optional[str] = None,
  country: Optional[str] = None,
) -> Dict[str, Any]:
  """
  Build a complete Place object with optional address and coordinates.

  Args:
    location_id: IRI (@id value)
    location_name: Place name
    latitude: Optional latitude
    longitude: Optional longitude
    city: Optional city
    state: Optional state
    country: Optional country

  Returns:
    Dict representing a Place with nested Address and GeoCoordinates
  """
  place = {
    "@type": "Place",
    "@id": location_id,
    "name": location_name,
  }

  # Add address if any component provided
  address = build_postal_address(city, state, country)
  if address:
    place["address"] = address

  # Add coordinates if both provided
  if latitude is not None and longitude is not None:
    place["geo"] = build_geo_coordinates(latitude, longitude)

  return place


def build_image_metadata(
  width: Optional[int] = None,
  height: Optional[int] = None,
  has_faces: Optional[bool] = None,
  latitude: Optional[float] = None,
  longitude: Optional[float] = None,
) -> Dict[str, Any]:
  """
  Build image-specific metadata for ImageObject.

  Args:
    width: Image width in pixels
    height: Image height in pixels
    has_faces: Whether faces are detected (custom extension, not schema.org standard)
    latitude: EXIF latitude (geo-tagging)
    longitude: EXIF longitude (geo-tagging)

  Returns:
    Dict with image properties (empty if all inputs are None)

  Note:
    The 'hasFaces' property is a custom extension and should be declared in the
    @context with a custom namespace if strict schema.org compliance is required.
    Example context entry:
      "ml": "https://example.org/ml-properties/",
    Then use: "ml:hasFaces" instead of "hasFaces"
  """
  metadata = {}

  if width is not None:
    metadata["width"] = width
  if height is not None:
    metadata["height"] = height
  if has_faces is not None:
    # Custom extension: face detection from ML model
    # Use "ml:hasFaces" if custom context is configured
    metadata["ml:hasFaces"] = has_faces
  if latitude is not None and longitude is not None:
    metadata["contentLocation"] = {
      "@type": "Place",
      "geo": build_geo_coordinates(latitude, longitude),
    }

  return metadata


def build_entity_mentions(
  companies: Optional[List[Any]] = None,
  people: Optional[List[Any]] = None,
) -> Optional[List[Dict[str, Any]]]:
  """
  Build mentions array from related entities.

  Args:
    companies: List of Company entities with get_iri() and name
    people: List of Person entities with get_iri() and name

  Returns:
    List of entity references, or None if no entities provided
  """
  mentions = []

  if companies:
    for company in companies:
      mentions.append(
        build_organization_reference(
          company.get_iri(),
          company.name,
        )
      )

  if people:
    for person in people:
      mentions.append(
        build_person_reference(
          person.get_iri(),
          person.name,
        )
      )

  return mentions if mentions else None


def build_spatial_coverage(
  locations: Optional[List[Any]],
) -> Optional[Any]:
  """
  Build spatialCoverage property from locations.

  Args:
    locations: List of Location entities with get_iri() and name

  Returns:
    Single Place object if 1 location, list if multiple, None if empty
  """
  if not locations:
    return None

  if len(locations) == 1:
    loc = locations[0]
    return build_location_reference(loc.get_iri(), loc.name)

  return [
    build_location_reference(loc.get_iri(), loc.name)
    for loc in locations
  ]

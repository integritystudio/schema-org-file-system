"""
MIME type to schema.org type mapping.

Provides deterministic mapping from file MIME types to appropriate
schema.org types (ImageObject, VideoObject, DigitalDocument, etc.).
"""

from typing import Optional


class MimeTypeMapper:
  """Map MIME types to schema.org types."""

  # Comprehensive MIME type → schema.org type mapping
  _TYPE_MAPPING = {
    # Images
    "image/jpeg": "ImageObject",
    "image/png": "ImageObject",
    "image/gif": "ImageObject",
    "image/svg+xml": "ImageObject",
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
    "text/x-typescript": "SoftwareSourceCode",
    "text/javascript": "SoftwareSourceCode",
  }

  # Prefix mappings for broader categories
  _PREFIX_MAPPINGS = {
    "image/": "ImageObject",
    "video/": "VideoObject",
    "audio/": "AudioObject",
    "text/": "DigitalDocument",
  }

  @staticmethod
  def get_schema_type(mime_type: Optional[str]) -> str:
    """
    Determine the appropriate schema.org type for a MIME type.

    Falls back to prefix matching if exact match not found.
    Returns "DigitalDocument" as final fallback.

    Args:
      mime_type: MIME type string (e.g., "application/pdf")

    Returns:
      Schema.org type name (e.g., "DigitalDocument", "ImageObject")
    """
    if not mime_type:
      return "DigitalDocument"

    # Try exact match first (case-insensitive)
    mime_lower = mime_type.lower()
    if mime_lower in MimeTypeMapper._TYPE_MAPPING:
      return MimeTypeMapper._TYPE_MAPPING[mime_lower]

    # Try prefix match
    for prefix, schema_type in MimeTypeMapper._PREFIX_MAPPINGS.items():
      if mime_lower.startswith(prefix):
        return schema_type

    # Final fallback
    return "DigitalDocument"

  @staticmethod
  def is_image(mime_type: Optional[str]) -> bool:
    """Check if MIME type is an image."""
    if not mime_type:
      return False
    return MimeTypeMapper.get_schema_type(mime_type) == "ImageObject"

  @staticmethod
  def is_video(mime_type: Optional[str]) -> bool:
    """Check if MIME type is a video."""
    if not mime_type:
      return False
    return MimeTypeMapper.get_schema_type(mime_type) == "VideoObject"

  @staticmethod
  def is_audio(mime_type: Optional[str]) -> bool:
    """Check if MIME type is audio."""
    if not mime_type:
      return False
    return MimeTypeMapper.get_schema_type(mime_type) == "AudioObject"

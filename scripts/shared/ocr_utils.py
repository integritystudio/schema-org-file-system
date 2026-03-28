"""Shared OCR text extraction."""
from __future__ import annotations
from pathlib import Path

OCR_AVAILABLE = False
_reader = None

try:
  import easyocr
  OCR_AVAILABLE = True
except ImportError:
  pass

# HEIC support
try:
  from pillow_heif import register_heif_opener
  register_heif_opener()
except ImportError:
  pass


def _get_reader():
  global _reader
  if _reader is None:
    _reader = easyocr.Reader(['en'], gpu=True, verbose=False)
  return _reader


def is_ocr_available() -> bool:
  return OCR_AVAILABLE


def extract_ocr_text(
  image_path: Path,
  max_chars: int = 500,
  config: str = "",         # kept for API compatibility, not used by easyocr
  timeout: int = 10,        # kept for API compatibility
) -> str | None:
  """Extract text from image using OCR.

  Uses easyocr (GPU-accelerated). The config and timeout parameters are
  kept for backward compatibility with callers but are ignored — easyocr
  manages its own decode pipeline.

  Returns None if OCR unavailable or no text found.
  """
  if not OCR_AVAILABLE:
    return None
  try:
    reader = _get_reader()
    results = reader.readtext(str(image_path), detail=0, paragraph=True)
    text = ' '.join(results)
    text = ' '.join(text.split())
    if max_chars and len(text) > max_chars:
      text = text[:max_chars] + "..."
    return text if text.strip() else None
  except Exception:
    return None

"""Shared OCR text extraction."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

OCR_AVAILABLE = False
try:
  import pytesseract
  from PIL import Image
  OCR_AVAILABLE = True
except ImportError:
  pass

# HEIC support
try:
  from pillow_heif import register_heif_opener
  register_heif_opener()
except ImportError:
  pass


def is_ocr_available() -> bool:
  return OCR_AVAILABLE


def extract_ocr_text(
  image_path: Path,
  max_chars: int = 500,
  config: str = "",
  timeout: int = 10,
) -> Optional[str]:
  """Extract text from image using OCR.

  Handles RGB conversion, text cleanup, and truncation.
  Returns None if OCR unavailable or no text found.
  """
  if not OCR_AVAILABLE:
    return None
  try:
    img = Image.open(image_path)
    if img.mode != 'RGB':
      img = img.convert('RGB')
    text = pytesseract.image_to_string(img, timeout=timeout, config=config)
    text = ' '.join(text.split())
    if max_chars and len(text) > max_chars:
      text = text[:max_chars] + "..."
    return text if text.strip() else None
  except Exception:
    return None

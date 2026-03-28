"""CLIP inference cache backed by joblib.Memory.

Caches classify() results by SHA-256 of image content so duplicate files
skip model inference entirely. Cache is stored in .cache/clip_embeddings/.
"""
from __future__ import annotations
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CLIP_CACHE_AVAILABLE = False
try:
  import joblib
  CLIP_CACHE_AVAILABLE = True
except ImportError:
  pass

_CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache" / "clip_embeddings"
_memory = joblib.Memory(location=_CACHE_DIR, verbose=0) if CLIP_CACHE_AVAILABLE else None


def _classify_by_hash(
  content_hash: str,
  image_path: Path,
  labels: list[str],
  prompt_prefix: str,
) -> list[tuple[str, float]]:
  # Deferred import avoids circular dependency at module load time.
  from shared.clip_utils import get_clip_classifier
  classifier = get_clip_classifier()
  return classifier.classify(image_path, labels, prompt_prefix)


if _memory is not None:
  _classify_by_hash = _memory.cache(_classify_by_hash)


def _sha256(path: Path) -> str:
  h = hashlib.sha256()
  with open(path, "rb") as f:
    for chunk in iter(lambda: f.read(65536), b""):
      h.update(chunk)
  return h.hexdigest()


def get_cached_embedding(
  image_path: Path,
  labels: list[str],
  prompt_prefix: str = "a photo of ",
) -> list[tuple[str, float]]:
  """Return classify() results, served from disk cache when possible.

  Cache key: SHA-256 of image file content + labels + prompt_prefix.
  Falls back to direct classify() call if joblib is not available.
  """
  if not CLIP_CACHE_AVAILABLE:
    from shared.clip_utils import get_clip_classifier
    return get_clip_classifier().classify(image_path, labels, prompt_prefix)

  content_hash = _sha256(image_path)
  return _classify_by_hash(content_hash, image_path, labels, prompt_prefix)

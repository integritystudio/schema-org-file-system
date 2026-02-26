"""CLIP model loading and classification utilities."""
from __future__ import annotations
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CLIP_AVAILABLE = False
try:
  import torch
  from transformers import CLIPProcessor, CLIPModel
  from PIL import Image
  CLIP_AVAILABLE = True
except ImportError:
  pass

# HEIC support
try:
  from pillow_heif import register_heif_opener
  register_heif_opener()
except ImportError:
  pass


class CLIPClassifier:
  """Shared CLIP model loader and classifier.

  Consolidates model loading + inference that was duplicated across
  analyze_renamed_files.py, image_content_analyzer.py,
  image_content_renamer.py, and screenshot_renamer.py.
  """

  MODEL_NAME = "openai/clip-vit-base-patch32"

  def __init__(self, device: str | None = None):
    if not CLIP_AVAILABLE:
      raise RuntimeError("CLIP not available. Install torch and transformers.")
    self.device = device or self._detect_device()
    logger.info("Loading CLIP model %s", self.MODEL_NAME)
    self.model = CLIPModel.from_pretrained(self.MODEL_NAME)
    self.processor = CLIPProcessor.from_pretrained(self.MODEL_NAME)
    self.model.to(self.device)
    self.model.eval()
    logger.info("CLIP model loaded (device: %s)", self.device)

  @staticmethod
  def _detect_device() -> str:
    if torch.backends.mps.is_available():
      return "mps"
    if torch.cuda.is_available():
      return "cuda"
    return "cpu"

  @staticmethod
  def is_available() -> bool:
    return CLIP_AVAILABLE

  def classify(
    self,
    image_path: Path,
    labels: list[str],
    prompt_prefix: str = "a photo of ",
  ) -> list[tuple[str, float]]:
    """Classify image against labels.

    Returns list of (label, confidence) sorted by confidence descending.
    """
    with Image.open(image_path) as img:
      image = img.convert("RGB")
    text_inputs = [f"{prompt_prefix}{lbl}" for lbl in labels]

    inputs = self.processor(
      text=text_inputs,
      images=image,
      return_tensors="pt",
      padding=True,
    )
    inputs = {k: v.to(self.device) for k, v in inputs.items()}

    with torch.no_grad():
      outputs = self.model(**inputs)
      probs = outputs.logits_per_image.softmax(dim=1)

    results = [(labels[i], probs[0][i].item()) for i in range(len(labels))]
    results.sort(key=lambda x: x[1], reverse=True)
    return results

  def classify_raw(
    self,
    image_path: Path,
    text_prompts: list[str],
  ) -> list[tuple[str, float]]:
    """Classify image using raw text prompts (no prefix added).

    Useful when labels already include "a photo of" etc.
    Returns list of (prompt, confidence) sorted by confidence descending.
    """
    with Image.open(image_path) as img:
      image = img.convert("RGB")

    inputs = self.processor(
      text=text_prompts,
      images=image,
      return_tensors="pt",
      padding=True,
    )
    inputs = {k: v.to(self.device) for k, v in inputs.items()}

    with torch.no_grad():
      outputs = self.model(**inputs)
      probs = outputs.logits_per_image.softmax(dim=1)

    results = [(text_prompts[i], probs[0][i].item()) for i in range(len(text_prompts))]
    results.sort(key=lambda x: x[1], reverse=True)
    return results

  def top_match(
    self,
    image_path: Path,
    labels: list[str],
    prompt_prefix: str = "a photo of ",
  ) -> tuple[str, float]:
    """Return single best match (label, confidence)."""
    results = self.classify(image_path, labels, prompt_prefix)
    return results[0] if results else ("unknown", 0.0)

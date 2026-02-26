"""Shared file operation utilities."""
from pathlib import Path


def resolve_collision(dest_path: Path) -> Path:
  """Resolve filename collision by appending incrementing counter.

  Given /foo/bar.png where bar.png exists, returns /foo/bar_1.png, etc.
  """
  if not dest_path.exists():
    return dest_path
  stem = dest_path.stem
  ext = dest_path.suffix
  parent = dest_path.parent
  counter = 1
  while dest_path.exists():
    dest_path = parent / f"{stem}_{counter}{ext}"
    counter += 1
  return dest_path

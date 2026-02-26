"""Shared database connection utilities."""
from __future__ import annotations
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "results" / "file_organization.db"


def get_db_connection(
  db_path: Path | str | None = None,
  row_factory: bool = True,
) -> sqlite3.Connection:
  """Get a SQLite connection.

  Args:
    db_path: Path to database. Defaults to results/file_organization.db
    row_factory: If True, set row_factory to sqlite3.Row
  """
  path = Path(db_path) if db_path else DEFAULT_DB_PATH
  conn = sqlite3.connect(str(path))
  if row_factory:
    conn.row_factory = sqlite3.Row
  return conn

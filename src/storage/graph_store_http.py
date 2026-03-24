#!/usr/bin/env python3
"""
HTTP-based GraphStore client for remote D1 database via Cloudflare Workers.

Provides same interface as graph_store.py but communicates with remote API.
Supports both local development (localhost) and production endpoints.

Usage:
  from storage.graph_store_http import GraphStoreHTTP
  store = GraphStoreHTTP("https://api.file-org.dev")
  file = store.add_file("/path/to/file.txt", "file.txt")
"""

import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from .models import FileStatus, RelationshipType


class GraphStoreHTTP:
  """HTTP client for remote D1 database."""

  def __init__(self, base_url: str = "http://localhost:8787", timeout: int = 30):
    """
    Initialize HTTP client.

    Args:
      base_url: Worker API base URL (e.g., https://api.file-org.dev or http://localhost:8787)
      timeout: Request timeout in seconds
    """
    self.base_url = base_url.rstrip('/')
    self.timeout = timeout
    self.session = requests.Session()

  def _request(
    self,
    method: str,
    path: str,
    data: Dict = None,
    params: Dict = None
  ) -> Dict[str, Any]:
    """Make HTTP request to API."""
    url = f"{self.base_url}{path}"

    try:
      if method == 'GET':
        resp = self.session.get(url, params=params, timeout=self.timeout)
      elif method == 'POST':
        resp = self.session.post(url, json=data, timeout=self.timeout)
      elif method == 'PUT':
        resp = self.session.put(url, json=data, timeout=self.timeout)
      elif method == 'DELETE':
        resp = self.session.delete(url, timeout=self.timeout)
      else:
        raise ValueError(f"Unsupported method: {method}")

      resp.raise_for_status()
      return resp.json()

    except requests.exceptions.RequestException as e:
      raise Exception(f"API request failed: {e}")

  # =========================================================================
  # File Operations
  # =========================================================================

  def add_file(
    self,
    original_path: str,
    filename: str,
    **kwargs
  ) -> Dict[str, Any]:
    """Add a new file to the store."""
    from .models import File

    file_id = File.generate_id(original_path)
    canonical_id = File.generate_canonical_id(original_path)

    body = {
      'id': file_id,
      'canonical_id': canonical_id,
      'filename': filename,
      'original_path': original_path,
      'file_extension': Path(filename).suffix.lower() if filename else None,
      **kwargs
    }

    result = self._request('POST', '/api/files', data=body)
    return result

  def get_file(self, file_id: str = None, path: str = None) -> Optional[Dict]:
    """Get a file by ID or path."""
    from .models import File

    if file_id:
      result = self._request('GET', f'/api/files/{file_id}')
    elif path:
      file_id = File.generate_id(path)
      result = self._request('GET', f'/api/files/{file_id}')
    else:
      return None

    return result if result else None

  def get_files(
    self,
    status: FileStatus = None,
    category: str = None,
    company: str = None,
    extension: str = None,
    limit: int = 100,
    offset: int = 0
  ) -> List[Dict[str, Any]]:
    """Query files with filters."""
    params = {
      'limit': str(limit),
      'offset': str(offset)
    }

    if status:
      params['status'] = status.value if isinstance(status, Enum) else status
    if category:
      params['category'] = category
    if company:
      params['company'] = company
    if extension:
      params['extension'] = extension.lower()

    result = self._request('GET', '/api/files', params=params)
    return result.get('results', []) if isinstance(result, dict) else result

  def update_file_status(
    self,
    file_id: str,
    status: FileStatus,
    destination: str = None,
    reason: str = None
  ) -> bool:
    """Update file organization status."""
    body = {
      'status': status.value if isinstance(status, Enum) else status,
      'destination': destination,
      'reason': reason
    }

    try:
      self._request('PUT', f'/api/files/{file_id}/status', data=body)
      return True
    except Exception:
      return False

  # =========================================================================
  # Category Operations
  # =========================================================================

  def get_or_create_category(
    self,
    name: str,
    parent_name: str = None
  ) -> Optional[Dict]:
    """Get or create a category."""
    body = {
      'name': name,
      'parent_name': parent_name
    }

    result = self._request('POST', '/api/categories', data=body)
    return result if result else None

  def get_category_tree(self) -> List[Dict[str, Any]]:
    """Get the full category hierarchy as a tree."""
    result = self._request('GET', '/api/categories')
    return result if isinstance(result, list) else []

  # =========================================================================
  # Statistics
  # =========================================================================

  def get_statistics(self) -> Dict[str, Any]:
    """Get overall statistics."""
    return self._request('GET', '/api/stats')

  # =========================================================================
  # Search
  # =========================================================================

  def search_files(
    self,
    query: str,
    limit: int = 50
  ) -> List[Dict[str, Any]]:
    """Search files by text."""
    result = self._request('GET', '/api/search', params={'q': query, 'limit': str(limit)})
    return result.get('results', []) if isinstance(result, dict) else result

  # =========================================================================
  # Health Check
  # =========================================================================

  def health(self) -> Dict[str, Any]:
    """Check API health."""
    return self._request('GET', '/health')

  # =========================================================================
  # Context Manager Support
  # =========================================================================

  def __enter__(self):
    return self

  def __exit__(self, *args):
    self.session.close()

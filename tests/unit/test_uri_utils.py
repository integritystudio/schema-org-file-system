#!/usr/bin/env python3
"""
Unit tests for src/uri_utils.py - URI generation utilities.

Priority: P1-3 (Medium - URI generation)
Coverage: 95%+ target

Tests IRI generation for Schema.org @id fields including:
- File IRIs (content-addressed)
- Canonical IRIs (deterministic)
- Random IRIs
- IRI validation and normalization
"""

import uuid
from pathlib import Path

import pytest

from src.uri_utils import (
    NAMESPACES,
    BASE_URI,
    generate_file_iri,
    generate_canonical_iri,
    generate_random_iri,
    generate_entity_url,
    is_valid_iri,
    normalize_to_iri,
    extract_uuid_from_iri,
    generate_merge_event_id,
    generate_same_as_jsonld,
)


class TestNamespacesConstant:
    """Test NAMESPACES constant is properly defined."""

    def test_namespaces_has_required_keys(self):
        """Should have all required namespace keys."""
        required_keys = ['file', 'category', 'company', 'person', 'location', 'session', 'merge_event']
        for key in required_keys:
            assert key in NAMESPACES, f"Missing namespace: {key}"

    def test_namespaces_are_valid_uuids(self):
        """All namespace values should be valid UUIDs."""
        for name, ns_uuid in NAMESPACES.items():
            assert isinstance(ns_uuid, uuid.UUID), f"{name} namespace is not a UUID"

    def test_namespaces_are_unique(self):
        """All namespace UUIDs should be unique."""
        values = list(NAMESPACES.values())
        assert len(values) == len(set(values)), "Duplicate namespace UUIDs found"


class TestGenerateFileIRI:
    """Test generate_file_iri function."""

    def test_generate_file_iri_with_hash(self):
        """Should generate urn:sha256: IRI by default."""
        iri = generate_file_iri('/path/to/document.pdf')
        assert iri.startswith('urn:sha256:')
        assert len(iri) == len('urn:sha256:') + 64  # SHA256 is 64 hex chars

    def test_generate_file_iri_without_hash(self):
        """Should generate HTTPS URL when use_hash=False."""
        iri = generate_file_iri('/path/to/document.pdf', use_hash=False)
        assert iri.startswith(BASE_URI)
        assert '/files/' in iri

    def test_generate_file_iri_is_deterministic(self):
        """Same path should always generate same IRI."""
        path = '/Users/test/documents/report.pdf'
        iri1 = generate_file_iri(path)
        iri2 = generate_file_iri(path)
        assert iri1 == iri2

    def test_generate_file_iri_different_paths_different_iris(self):
        """Different paths should generate different IRIs."""
        iri1 = generate_file_iri('/path/to/file1.pdf')
        iri2 = generate_file_iri('/path/to/file2.pdf')
        assert iri1 != iri2

    def test_generate_file_iri_normalizes_path(self):
        """Should normalize relative paths to absolute."""
        # This test depends on current working directory
        # but the function should resolve to absolute path
        iri = generate_file_iri('relative/path/file.txt')
        assert iri.startswith('urn:sha256:')

    def test_generate_file_iri_url_safe(self):
        """HTTPS URL should be URL-safe encoded."""
        iri = generate_file_iri('/path with spaces/file.pdf', use_hash=False)
        assert ' ' not in iri  # Spaces should be encoded


class TestGenerateCanonicalIRI:
    """Test generate_canonical_iri function."""

    def test_generate_canonical_iri_company(self):
        """Should generate deterministic IRI for company."""
        iri = generate_canonical_iri('company', 'Acme Corporation')
        assert iri.startswith('urn:uuid:')
        # UUID v5 should be valid
        uuid_str = iri.replace('urn:uuid:', '')
        uuid.UUID(uuid_str)  # Will raise if invalid

    def test_generate_canonical_iri_person(self):
        """Should generate deterministic IRI for person."""
        iri = generate_canonical_iri('person', 'John Doe')
        assert iri.startswith('urn:uuid:')

    def test_generate_canonical_iri_location(self):
        """Should generate deterministic IRI for location."""
        iri = generate_canonical_iri('location', 'New York City')
        assert iri.startswith('urn:uuid:')

    def test_generate_canonical_iri_category(self):
        """Should generate deterministic IRI for category."""
        iri = generate_canonical_iri('category', 'GameAssets/Sprites')
        assert iri.startswith('urn:uuid:')

    def test_generate_canonical_iri_is_deterministic(self):
        """Same inputs should always produce same IRI."""
        iri1 = generate_canonical_iri('company', 'Acme Corporation')
        iri2 = generate_canonical_iri('company', 'Acme Corporation')
        assert iri1 == iri2

    def test_generate_canonical_iri_case_insensitive(self):
        """Should be case-insensitive."""
        iri1 = generate_canonical_iri('company', 'ACME')
        iri2 = generate_canonical_iri('company', 'acme')
        iri3 = generate_canonical_iri('company', 'Acme')
        assert iri1 == iri2 == iri3

    def test_generate_canonical_iri_trims_whitespace(self):
        """Should trim whitespace from natural key."""
        iri1 = generate_canonical_iri('person', 'John Doe')
        iri2 = generate_canonical_iri('person', '  John Doe  ')
        assert iri1 == iri2

    def test_generate_canonical_iri_different_types_different_iris(self):
        """Same name with different types should produce different IRIs."""
        iri_company = generate_canonical_iri('company', 'Smith')
        iri_person = generate_canonical_iri('person', 'Smith')
        iri_location = generate_canonical_iri('location', 'Smith')
        assert iri_company != iri_person
        assert iri_person != iri_location
        assert iri_company != iri_location

    def test_generate_canonical_iri_case_insensitive_entity_type(self):
        """Entity type should be case-insensitive."""
        iri1 = generate_canonical_iri('COMPANY', 'Acme')
        iri2 = generate_canonical_iri('company', 'Acme')
        iri3 = generate_canonical_iri('Company', 'Acme')
        assert iri1 == iri2 == iri3

    def test_generate_canonical_iri_unknown_type_raises(self):
        """Should raise ValueError for unknown entity type."""
        with pytest.raises(ValueError) as exc_info:
            generate_canonical_iri('unknown_type', 'test')
        assert 'Unknown entity type' in str(exc_info.value)
        assert 'unknown_type' in str(exc_info.value)


class TestGenerateRandomIRI:
    """Test generate_random_iri function."""

    def test_generate_random_iri_default(self):
        """Should generate urn:uuid: IRI by default."""
        iri = generate_random_iri()
        assert iri.startswith('urn:uuid:')
        # Validate UUID
        uuid_str = iri.replace('urn:uuid:', '')
        uuid.UUID(uuid_str)

    def test_generate_random_iri_with_entity_type(self):
        """Should generate entity URL when type provided."""
        iri = generate_random_iri('company')
        assert iri.startswith(BASE_URI)
        assert '/companies/' in iri

    def test_generate_random_iri_unique_each_call(self):
        """Each call should generate unique IRI."""
        iris = [generate_random_iri() for _ in range(100)]
        assert len(set(iris)) == 100  # All unique


class TestGenerateEntityURL:
    """Test generate_entity_url function."""

    def test_generate_entity_url_company(self):
        """Should generate URL for company entity."""
        url = generate_entity_url('company', 'abc123')
        assert url == f'{BASE_URI}/companies/abc123'

    def test_generate_entity_url_person(self):
        """Should generate URL for person entity."""
        url = generate_entity_url('person', 'def456')
        assert url == f'{BASE_URI}/persons/def456'

    def test_generate_entity_url_category(self):
        """Should generate URL for category entity."""
        url = generate_entity_url('category', 'ghi789')
        assert url == f'{BASE_URI}/categories/ghi789'

    def test_generate_entity_url_location(self):
        """Should generate URL for location entity."""
        url = generate_entity_url('location', 'jkl012')
        assert url == f'{BASE_URI}/locations/jkl012'

    def test_generate_entity_url_file(self):
        """Should generate URL for file entity."""
        url = generate_entity_url('file', 'mno345')
        assert url == f'{BASE_URI}/files/mno345'

    def test_generate_entity_url_unknown_type(self):
        """Should pluralize unknown types with 's'."""
        url = generate_entity_url('widget', 'pqr678')
        assert url == f'{BASE_URI}/widgets/pqr678'

    def test_generate_entity_url_case_insensitive(self):
        """Entity type should be case-insensitive."""
        url1 = generate_entity_url('COMPANY', 'test')
        url2 = generate_entity_url('company', 'test')
        assert url1 == url2


class TestIsValidIRI:
    """Test is_valid_iri function."""

    def test_is_valid_iri_https(self):
        """Should accept HTTPS URLs."""
        assert is_valid_iri('https://example.com/entity/123')
        assert is_valid_iri('https://schema.org/Person')

    def test_is_valid_iri_http(self):
        """Should accept HTTP URLs."""
        assert is_valid_iri('http://example.com/entity/123')

    def test_is_valid_iri_urn_uuid(self):
        """Should accept urn:uuid: IRIs."""
        assert is_valid_iri('urn:uuid:550e8400-e29b-41d4-a716-446655440000')

    def test_is_valid_iri_urn_sha256(self):
        """Should accept urn:sha256: IRIs."""
        assert is_valid_iri('urn:sha256:abc123def456')

    def test_is_valid_iri_urn_isbn(self):
        """Should accept urn:isbn: IRIs."""
        assert is_valid_iri('urn:isbn:978-3-16-148410-0')

    def test_is_valid_iri_urn_issn(self):
        """Should accept urn:issn: IRIs."""
        assert is_valid_iri('urn:issn:1234-5678')

    def test_is_valid_iri_urn_doi(self):
        """Should accept urn:doi: IRIs."""
        assert is_valid_iri('urn:doi:10.1000/xyz123')

    def test_is_valid_iri_rejects_plain_string(self):
        """Should reject plain strings."""
        assert not is_valid_iri('just-a-string')
        assert not is_valid_iri('some text here')

    def test_is_valid_iri_rejects_empty(self):
        """Should reject empty string."""
        assert not is_valid_iri('')

    def test_is_valid_iri_rejects_none(self):
        """Should reject None."""
        assert not is_valid_iri(None)

    def test_is_valid_iri_rejects_non_string(self):
        """Should reject non-string types."""
        assert not is_valid_iri(123)
        assert not is_valid_iri(['list'])
        assert not is_valid_iri({'dict': 'value'})


class TestNormalizeToIRI:
    """Test normalize_to_iri function."""

    def test_normalize_already_valid_https(self):
        """Should return valid HTTPS IRI unchanged."""
        iri = 'https://example.com/entity/123'
        assert normalize_to_iri(iri) == iri

    def test_normalize_already_valid_urn_uuid(self):
        """Should return valid urn:uuid: IRI unchanged."""
        iri = 'urn:uuid:550e8400-e29b-41d4-a716-446655440000'
        assert normalize_to_iri(iri) == iri

    def test_normalize_already_valid_urn_sha256(self):
        """Should return valid urn:sha256: IRI unchanged."""
        iri = 'urn:sha256:abc123def456'
        assert normalize_to_iri(iri) == iri

    def test_normalize_uuid_string(self):
        """Should wrap UUID string in urn:uuid:."""
        uuid_str = '550e8400-e29b-41d4-a716-446655440000'
        result = normalize_to_iri(uuid_str)
        assert result == f'urn:uuid:{uuid_str}'

    def test_normalize_sha256_hash(self):
        """Should wrap 64-char hex string in urn:sha256:."""
        hash_str = 'a' * 64  # 64 hex characters
        result = normalize_to_iri(hash_str)
        assert result == f'urn:sha256:{hash_str}'

    def test_normalize_sha256_mixed_case(self):
        """Should handle mixed case hex strings."""
        hash_str = 'AbCdEf' + 'a' * 58  # 64 hex characters
        result = normalize_to_iri(hash_str)
        assert result.startswith('urn:sha256:')

    def test_normalize_arbitrary_string(self):
        """Should create deterministic IRI from arbitrary string."""
        result = normalize_to_iri('some random string')
        assert result.startswith('urn:uuid:')
        # Should be deterministic
        assert result == normalize_to_iri('some random string')


class TestExtractUUIDFromIRI:
    """Test extract_uuid_from_iri function."""

    def test_extract_from_urn_uuid(self):
        """Should extract UUID from urn:uuid: IRI."""
        uuid_str = '550e8400-e29b-41d4-a716-446655440000'
        iri = f'urn:uuid:{uuid_str}'
        assert extract_uuid_from_iri(iri) == uuid_str

    def test_extract_from_https_url(self):
        """Should extract last path segment from HTTPS URL."""
        iri = 'https://example.com/entities/abc-123-def'
        assert extract_uuid_from_iri(iri) == 'abc-123-def'

    def test_extract_from_https_url_trailing_slash(self):
        """Should handle trailing slash in URL."""
        iri = 'https://example.com/entities/abc-123-def/'
        assert extract_uuid_from_iri(iri) == 'abc-123-def'

    def test_extract_from_http_url(self):
        """Should extract from HTTP URL."""
        iri = 'http://example.com/entities/xyz789'
        assert extract_uuid_from_iri(iri) == 'xyz789'

    def test_extract_from_urn_sha256_returns_none(self):
        """Should return None for urn:sha256: (not a UUID)."""
        iri = 'urn:sha256:abc123def456'
        assert extract_uuid_from_iri(iri) is None

    def test_extract_from_empty_returns_none(self):
        """Should return None for empty string."""
        assert extract_uuid_from_iri('') is None

    def test_extract_from_none_returns_none(self):
        """Should return None for None."""
        assert extract_uuid_from_iri(None) is None


class TestGenerateMergeEventID:
    """Test generate_merge_event_id function."""

    def test_generate_merge_event_id_format(self):
        """Should generate urn:uuid: format."""
        event_id = generate_merge_event_id()
        assert event_id.startswith('urn:uuid:')

    def test_generate_merge_event_id_unique(self):
        """Each call should generate unique ID."""
        ids = [generate_merge_event_id() for _ in range(100)]
        assert len(set(ids)) == 100

    def test_generate_merge_event_id_valid_uuid(self):
        """Should contain valid UUID."""
        event_id = generate_merge_event_id()
        uuid_str = event_id.replace('urn:uuid:', '')
        uuid.UUID(uuid_str)  # Will raise if invalid


class TestGenerateSameAsJSONLD:
    """Test generate_same_as_jsonld function."""

    def test_generate_same_as_single_merged(self):
        """Should generate JSON-LD with single merged IRI."""
        result = generate_same_as_jsonld(
            'urn:uuid:canonical-123',
            ['urn:uuid:merged-1']
        )
        assert result['@id'] == 'urn:uuid:canonical-123'
        assert result['owl:sameAs'] == 'urn:uuid:merged-1'

    def test_generate_same_as_multiple_merged(self):
        """Should generate JSON-LD with multiple merged IRIs."""
        result = generate_same_as_jsonld(
            'urn:uuid:canonical-123',
            ['urn:uuid:merged-1', 'urn:uuid:merged-2', 'urn:uuid:merged-3']
        )
        assert result['@id'] == 'urn:uuid:canonical-123'
        assert result['owl:sameAs'] == ['urn:uuid:merged-1', 'urn:uuid:merged-2', 'urn:uuid:merged-3']

    def test_generate_same_as_preserves_iri_format(self):
        """Should preserve various IRI formats."""
        result = generate_same_as_jsonld(
            'https://example.com/canonical',
            ['urn:sha256:abc123', 'https://other.com/entity']
        )
        assert result['@id'] == 'https://example.com/canonical'
        assert 'urn:sha256:abc123' in result['owl:sameAs']
        assert 'https://other.com/entity' in result['owl:sameAs']


class TestIDConsistency:
    """Test consistency of ID generation across functions."""

    def test_same_company_same_id_from_canonical_and_namespaces(self):
        """Canonical IRI should match manual UUID v5 generation with company namespace."""
        company_name = 'Test Company Inc'
        canonical_iri = generate_canonical_iri('company', company_name)

        # Manually compute with namespace
        expected_uuid = uuid.uuid5(NAMESPACES['company'], company_name.lower().strip())
        expected_iri = f'urn:uuid:{expected_uuid}'

        assert canonical_iri == expected_iri

    def test_same_person_same_id_from_canonical_and_namespaces(self):
        """Canonical IRI should match manual UUID v5 generation with person namespace."""
        person_name = 'John Smith'
        canonical_iri = generate_canonical_iri('person', person_name)

        expected_uuid = uuid.uuid5(NAMESPACES['person'], person_name.lower().strip())
        expected_iri = f'urn:uuid:{expected_uuid}'

        assert canonical_iri == expected_iri

    def test_file_iri_stable_across_sessions(self):
        """File IRI should be stable (same hash for same path)."""
        # This simulates calling the function in different sessions
        path = '/test/path/to/file.pdf'
        iri1 = generate_file_iri(path)
        iri2 = generate_file_iri(path)
        iri3 = generate_file_iri(path)
        assert iri1 == iri2 == iri3

#!/usr/bin/env python3
"""
Unit tests for src/base.py - Schema.org base classes.

Priority: P1-1 (High - Core Schema.org generation)
Coverage: 90%+ target

Tests base classes for Schema.org generation including:
- SchemaContext
- PropertyType enum
- SchemaOrgBase abstract class
"""

import json
import uuid
from datetime import datetime
from typing import List

import pytest

from src.base import SchemaContext, PropertyType, SchemaOrgBase


class TestSchemaContext:
    """Test SchemaContext class."""

    def test_schema_org_constant(self):
        """Should have Schema.org URL constant."""
        assert SchemaContext.SCHEMA_ORG == "https://schema.org"

    def test_default_context_has_required_keys(self):
        """Default context should have @context and @vocab."""
        assert "@context" in SchemaContext.DEFAULT_CONTEXT
        assert "@vocab" in SchemaContext.DEFAULT_CONTEXT

    def test_get_context_returns_default(self):
        """get_context without args should return default context."""
        context = SchemaContext.get_context()
        assert context["@context"] == "https://schema.org"
        assert context["@vocab"] == "https://schema.org/"

    def test_get_context_with_additional(self):
        """get_context with additional contexts should merge them."""
        additional = {"custom": "http://example.com/custom"}
        context = SchemaContext.get_context(additional)

        assert context["@context"] == "https://schema.org"
        assert context["custom"] == "http://example.com/custom"

    def test_get_context_does_not_modify_default(self):
        """get_context should not modify DEFAULT_CONTEXT."""
        original = SchemaContext.DEFAULT_CONTEXT.copy()
        SchemaContext.get_context({"extra": "value"})
        assert SchemaContext.DEFAULT_CONTEXT == original


class TestPropertyType:
    """Test PropertyType enum."""

    def test_all_property_types_exist(self):
        """Should have all expected property types."""
        expected_types = [
            'TEXT', 'URL', 'DATE', 'DATETIME', 'NUMBER',
            'INTEGER', 'BOOLEAN', 'OBJECT', 'ARRAY'
        ]
        for type_name in expected_types:
            assert hasattr(PropertyType, type_name)

    def test_property_type_values(self):
        """Property types should have correct string values."""
        assert PropertyType.TEXT.value == "Text"
        assert PropertyType.URL.value == "URL"
        assert PropertyType.DATE.value == "Date"
        assert PropertyType.DATETIME.value == "DateTime"
        assert PropertyType.NUMBER.value == "Number"
        assert PropertyType.INTEGER.value == "Integer"
        assert PropertyType.BOOLEAN.value == "Boolean"
        assert PropertyType.OBJECT.value == "Object"
        assert PropertyType.ARRAY.value == "Array"


class ConcreteSchema(SchemaOrgBase):
    """Concrete implementation of SchemaOrgBase for testing."""

    def get_required_properties(self) -> List[str]:
        return ['name']

    def get_recommended_properties(self) -> List[str]:
        return ['description', 'url']


class TestSchemaOrgBaseInit:
    """Test SchemaOrgBase initialization."""

    def test_init_sets_schema_type(self):
        """Should set the schema type."""
        schema = ConcreteSchema('Thing')
        assert schema.schema_type == 'Thing'
        assert schema.data['@type'] == 'Thing'

    def test_init_sets_context(self):
        """Should set Schema.org context."""
        schema = ConcreteSchema('Thing')
        assert schema.data['@context'] == 'https://schema.org'

    def test_init_generates_uuid_id_when_none(self):
        """Should generate UUID v4 @id when entity_id is None."""
        schema = ConcreteSchema('Thing')
        assert '@id' in schema.data
        assert schema.data['@id'].startswith('urn:uuid:')
        # Validate the UUID
        uuid_str = schema.data['@id'].replace('urn:uuid:', '')
        uuid.UUID(uuid_str)  # Will raise if invalid

    def test_init_accepts_uuid_string(self):
        """Should wrap plain UUID string in urn:uuid:."""
        uuid_str = '550e8400-e29b-41d4-a716-446655440000'
        schema = ConcreteSchema('Thing', entity_id=uuid_str)
        assert schema.data['@id'] == f'urn:uuid:{uuid_str}'

    def test_init_accepts_urn_uuid(self):
        """Should accept urn:uuid: IRI directly."""
        iri = 'urn:uuid:550e8400-e29b-41d4-a716-446655440000'
        schema = ConcreteSchema('Thing', entity_id=iri)
        assert schema.data['@id'] == iri

    def test_init_accepts_urn_sha256(self):
        """Should accept urn:sha256: IRI directly."""
        iri = 'urn:sha256:abc123def456'
        schema = ConcreteSchema('Thing', entity_id=iri)
        assert schema.data['@id'] == iri

    def test_init_accepts_https_url(self):
        """Should accept HTTPS URL directly."""
        url = 'https://example.com/entity/123'
        schema = ConcreteSchema('Thing', entity_id=url)
        assert schema.data['@id'] == url

    def test_init_accepts_http_url(self):
        """Should accept HTTP URL directly."""
        url = 'http://example.com/entity/123'
        schema = ConcreteSchema('Thing', entity_id=url)
        assert schema.data['@id'] == url

    def test_init_creates_empty_required_properties(self):
        """Should initialize required properties list."""
        schema = ConcreteSchema('Thing')
        assert hasattr(schema, '_required_properties')

    def test_init_creates_empty_recommended_properties(self):
        """Should initialize recommended properties list."""
        schema = ConcreteSchema('Thing')
        assert hasattr(schema, '_recommended_properties')


class TestSchemaOrgBaseSetProperty:
    """Test set_property method."""

    def test_set_property_basic(self):
        """Should set a basic property."""
        schema = ConcreteSchema('Thing')
        schema.set_property('name', 'Test Name')
        assert schema.data['name'] == 'Test Name'

    def test_set_property_returns_self(self):
        """Should return self for method chaining."""
        schema = ConcreteSchema('Thing')
        result = schema.set_property('name', 'Test')
        assert result is schema

    def test_set_property_none_value_skipped(self):
        """Should skip setting None values."""
        schema = ConcreteSchema('Thing')
        schema.set_property('name', None)
        assert 'name' not in schema.data

    def test_set_property_text_type(self):
        """Should convert to string with TEXT type."""
        schema = ConcreteSchema('Thing')
        schema.set_property('name', 123, PropertyType.TEXT)
        assert schema.data['name'] == '123'

    def test_set_property_url_type_valid(self):
        """Should accept valid URL with URL type."""
        schema = ConcreteSchema('Thing')
        schema.set_property('url', 'https://example.com', PropertyType.URL)
        assert schema.data['url'] == 'https://example.com'

    def test_set_property_url_type_invalid_raises(self):
        """Should raise ValueError for invalid URL."""
        schema = ConcreteSchema('Thing')
        with pytest.raises(ValueError) as exc_info:
            schema.set_property('url', 'not-a-url', PropertyType.URL)
        assert 'Invalid URL' in str(exc_info.value)

    def test_set_property_date_type_datetime(self):
        """Should convert datetime to ISO date string."""
        schema = ConcreteSchema('Thing')
        dt = datetime(2024, 6, 15, 10, 30, 0)
        schema.set_property('dateCreated', dt, PropertyType.DATE)
        assert schema.data['dateCreated'] == '2024-06-15'

    def test_set_property_date_type_string(self):
        """Should pass string dates through."""
        schema = ConcreteSchema('Thing')
        schema.set_property('dateCreated', '2024-06-15', PropertyType.DATE)
        assert schema.data['dateCreated'] == '2024-06-15'

    def test_set_property_datetime_type(self):
        """Should convert datetime to ISO datetime string."""
        schema = ConcreteSchema('Thing')
        dt = datetime(2024, 6, 15, 10, 30, 0)
        schema.set_property('dateCreated', dt, PropertyType.DATETIME)
        assert schema.data['dateCreated'] == '2024-06-15T10:30:00'

    def test_set_property_number_type(self):
        """Should convert to float with NUMBER type."""
        schema = ConcreteSchema('Thing')
        schema.set_property('price', '99.99', PropertyType.NUMBER)
        assert schema.data['price'] == 99.99

    def test_set_property_integer_type(self):
        """Should convert to int with INTEGER type."""
        schema = ConcreteSchema('Thing')
        schema.set_property('count', '42', PropertyType.INTEGER)
        assert schema.data['count'] == 42

    def test_set_property_boolean_type(self):
        """Should convert to bool with BOOLEAN type."""
        schema = ConcreteSchema('Thing')
        schema.set_property('active', 1, PropertyType.BOOLEAN)
        assert schema.data['active'] is True

    def test_set_property_object_type_valid(self):
        """Should accept dict with OBJECT type."""
        schema = ConcreteSchema('Thing')
        obj = {'@type': 'Person', 'name': 'John'}
        schema.set_property('author', obj, PropertyType.OBJECT)
        assert schema.data['author'] == obj

    def test_set_property_object_type_invalid_raises(self):
        """Should raise ValueError for non-dict OBJECT type."""
        schema = ConcreteSchema('Thing')
        with pytest.raises(ValueError) as exc_info:
            schema.set_property('author', 'not-an-object', PropertyType.OBJECT)
        assert 'Expected object' in str(exc_info.value)

    def test_set_property_array_type_list(self):
        """Should pass list through with ARRAY type."""
        schema = ConcreteSchema('Thing')
        arr = ['a', 'b', 'c']
        schema.set_property('keywords', arr, PropertyType.ARRAY)
        assert schema.data['keywords'] == arr

    def test_set_property_array_type_single_value(self):
        """Should wrap single value in array with ARRAY type."""
        schema = ConcreteSchema('Thing')
        schema.set_property('keywords', 'single', PropertyType.ARRAY)
        assert schema.data['keywords'] == ['single']


class TestSchemaOrgBaseNestedSchema:
    """Test add_nested_schema method."""

    def test_add_nested_schema(self):
        """Should add nested schema as dict."""
        parent = ConcreteSchema('Thing')
        child = ConcreteSchema('Person')
        child.set_property('name', 'John Doe')

        parent.add_nested_schema('author', child)

        assert 'author' in parent.data
        assert parent.data['author']['@type'] == 'Person'
        assert parent.data['author']['name'] == 'John Doe'

    def test_add_nested_schema_returns_self(self):
        """Should return self for method chaining."""
        parent = ConcreteSchema('Thing')
        child = ConcreteSchema('Person')
        result = parent.add_nested_schema('author', child)
        assert result is parent


class TestSchemaOrgBaseSetID:
    """Test set_id and get_id methods."""

    def test_set_id_with_urn_uuid(self):
        """Should set urn:uuid: IRI directly."""
        schema = ConcreteSchema('Thing')
        iri = 'urn:uuid:550e8400-e29b-41d4-a716-446655440000'
        schema.set_id(iri)
        assert schema.data['@id'] == iri

    def test_set_id_with_https_url(self):
        """Should set HTTPS URL directly."""
        schema = ConcreteSchema('Thing')
        url = 'https://example.com/entity/123'
        schema.set_id(url)
        assert schema.data['@id'] == url

    def test_set_id_with_plain_uuid(self):
        """Should wrap plain UUID in urn:uuid:."""
        schema = ConcreteSchema('Thing')
        uuid_str = '550e8400-e29b-41d4-a716-446655440000'
        schema.set_id(uuid_str)
        assert schema.data['@id'] == f'urn:uuid:{uuid_str}'

    def test_set_id_returns_self(self):
        """Should return self for method chaining."""
        schema = ConcreteSchema('Thing')
        result = schema.set_id('urn:uuid:test')
        assert result is schema

    def test_get_id(self):
        """Should return current @id."""
        iri = 'urn:uuid:550e8400-e29b-41d4-a716-446655440000'
        schema = ConcreteSchema('Thing', entity_id=iri)
        assert schema.get_id() == iri

    def test_get_id_empty_returns_empty_string(self):
        """Should return empty string if @id not set."""
        schema = ConcreteSchema('Thing')
        del schema.data['@id']  # Remove the auto-generated ID
        assert schema.get_id() == ''


class TestSchemaOrgBaseAddPerson:
    """Test add_person method."""

    def test_add_person_basic(self):
        """Should add Person with name and @id."""
        schema = ConcreteSchema('Thing')
        schema.add_person('author', 'John Doe')

        person = schema.data['author']
        assert person['@type'] == 'Person'
        assert person['name'] == 'John Doe'
        assert '@id' in person
        assert person['@id'].startswith('urn:uuid:')

    def test_add_person_with_email(self):
        """Should add email when provided."""
        schema = ConcreteSchema('Thing')
        schema.add_person('author', 'John Doe', email='john@example.com')
        assert schema.data['author']['email'] == 'john@example.com'

    def test_add_person_with_url(self):
        """Should add URL when provided."""
        schema = ConcreteSchema('Thing')
        schema.add_person('author', 'John Doe', url='https://johndoe.com')
        assert schema.data['author']['url'] == 'https://johndoe.com'

    def test_add_person_with_affiliation(self):
        """Should add Organization affiliation with @id."""
        schema = ConcreteSchema('Thing')
        schema.add_person('author', 'John Doe', affiliation='Acme Corp')

        person = schema.data['author']
        assert 'affiliation' in person
        assert person['affiliation']['@type'] == 'Organization'
        assert person['affiliation']['name'] == 'Acme Corp'
        assert '@id' in person['affiliation']

    def test_add_person_with_custom_id(self):
        """Should use custom person_id when provided."""
        schema = ConcreteSchema('Thing')
        custom_id = 'urn:uuid:custom-person-id'
        schema.add_person('author', 'John Doe', person_id=custom_id)
        assert schema.data['author']['@id'] == custom_id

    def test_add_person_wraps_plain_uuid(self):
        """Should wrap plain UUID in urn:uuid:."""
        schema = ConcreteSchema('Thing')
        schema.add_person('author', 'John Doe', person_id='custom-id')
        assert schema.data['author']['@id'] == 'urn:uuid:custom-id'

    def test_add_person_id_is_deterministic(self):
        """Same name should generate same @id."""
        schema1 = ConcreteSchema('Thing')
        schema2 = ConcreteSchema('Thing')
        schema1.add_person('author', 'Jane Smith')
        schema2.add_person('author', 'Jane Smith')
        assert schema1.data['author']['@id'] == schema2.data['author']['@id']

    def test_add_person_returns_self(self):
        """Should return self for method chaining."""
        schema = ConcreteSchema('Thing')
        result = schema.add_person('author', 'John Doe')
        assert result is schema


class TestSchemaOrgBaseAddOrganization:
    """Test add_organization method."""

    def test_add_organization_basic(self):
        """Should add Organization with name and @id."""
        schema = ConcreteSchema('Thing')
        schema.add_organization('publisher', 'Acme Corp')

        org = schema.data['publisher']
        assert org['@type'] == 'Organization'
        assert org['name'] == 'Acme Corp'
        assert '@id' in org
        assert org['@id'].startswith('urn:uuid:')

    def test_add_organization_with_url(self):
        """Should add URL when provided."""
        schema = ConcreteSchema('Thing')
        schema.add_organization('publisher', 'Acme Corp', url='https://acme.com')
        assert schema.data['publisher']['url'] == 'https://acme.com'

    def test_add_organization_with_logo(self):
        """Should add logo as ImageObject with @id."""
        schema = ConcreteSchema('Thing')
        schema.add_organization('publisher', 'Acme Corp', logo='https://acme.com/logo.png')

        org = schema.data['publisher']
        assert 'logo' in org
        assert org['logo']['@type'] == 'ImageObject'
        assert org['logo']['url'] == 'https://acme.com/logo.png'
        assert '@id' in org['logo']

    def test_add_organization_with_custom_id(self):
        """Should use custom org_id when provided."""
        schema = ConcreteSchema('Thing')
        custom_id = 'urn:uuid:custom-org-id'
        schema.add_organization('publisher', 'Acme Corp', org_id=custom_id)
        assert schema.data['publisher']['@id'] == custom_id

    def test_add_organization_id_is_deterministic(self):
        """Same name should generate same @id."""
        schema1 = ConcreteSchema('Thing')
        schema2 = ConcreteSchema('Thing')
        schema1.add_organization('publisher', 'Test Corp')
        schema2.add_organization('publisher', 'Test Corp')
        assert schema1.data['publisher']['@id'] == schema2.data['publisher']['@id']


class TestSchemaOrgBaseAddPlace:
    """Test add_place method."""

    def test_add_place_basic(self):
        """Should add Place with name and @id."""
        schema = ConcreteSchema('Thing')
        schema.add_place('contentLocation', 'New York City')

        place = schema.data['contentLocation']
        assert place['@type'] == 'Place'
        assert place['name'] == 'New York City'
        assert '@id' in place

    def test_add_place_with_address(self):
        """Should add address when provided."""
        schema = ConcreteSchema('Thing')
        schema.add_place('contentLocation', 'NYC', address='123 Main St, New York, NY')
        assert schema.data['contentLocation']['address'] == '123 Main St, New York, NY'

    def test_add_place_with_geo_coordinates(self):
        """Should add GeoCoordinates when geo provided."""
        schema = ConcreteSchema('Thing')
        geo = {'latitude': 40.7128, 'longitude': -74.0060}
        schema.add_place('contentLocation', 'NYC', geo=geo)

        place = schema.data['contentLocation']
        assert 'geo' in place
        assert place['geo']['@type'] == 'GeoCoordinates'
        assert place['geo']['latitude'] == 40.7128
        assert place['geo']['longitude'] == -74.0060

    def test_add_place_with_custom_id(self):
        """Should use custom place_id when provided."""
        schema = ConcreteSchema('Thing')
        custom_id = 'urn:uuid:custom-place-id'
        schema.add_place('contentLocation', 'NYC', place_id=custom_id)
        assert schema.data['contentLocation']['@id'] == custom_id


class TestSchemaOrgBaseIdentifier:
    """Test set_identifier method."""

    def test_set_identifier_simple(self):
        """Should set simple identifier string."""
        schema = ConcreteSchema('Thing')
        schema.set_identifier('ABC123')
        assert schema.data['identifier'] == 'ABC123'

    def test_set_identifier_with_property_id(self):
        """Should set PropertyValue identifier with propertyID."""
        schema = ConcreteSchema('Thing')
        schema.set_identifier('ISBN-123', property_id='ISBN')

        identifier = schema.data['identifier']
        assert identifier['@type'] == 'PropertyValue'
        assert identifier['propertyID'] == 'ISBN'
        assert identifier['value'] == 'ISBN-123'

    def test_set_identifier_returns_self(self):
        """Should return self for method chaining."""
        schema = ConcreteSchema('Thing')
        result = schema.set_identifier('test')
        assert result is schema


class TestSchemaOrgBaseKeywords:
    """Test add_keywords method."""

    def test_add_keywords_string(self):
        """Should set string keywords directly."""
        schema = ConcreteSchema('Thing')
        schema.add_keywords('python, programming, tutorial')
        assert schema.data['keywords'] == 'python, programming, tutorial'

    def test_add_keywords_list(self):
        """Should join list keywords with comma."""
        schema = ConcreteSchema('Thing')
        schema.add_keywords(['python', 'programming', 'tutorial'])
        assert schema.data['keywords'] == 'python, programming, tutorial'

    def test_add_keywords_returns_self(self):
        """Should return self for method chaining."""
        schema = ConcreteSchema('Thing')
        result = schema.add_keywords('test')
        assert result is schema


class TestSchemaOrgBaseDates:
    """Test set_dates method."""

    def test_set_dates_created(self):
        """Should set dateCreated."""
        schema = ConcreteSchema('Thing')
        dt = datetime(2024, 6, 15, 10, 30)
        schema.set_dates(created=dt)
        assert schema.data['dateCreated'] == '2024-06-15T10:30:00'

    def test_set_dates_modified(self):
        """Should set dateModified."""
        schema = ConcreteSchema('Thing')
        dt = datetime(2024, 6, 20, 14, 45)
        schema.set_dates(modified=dt)
        assert schema.data['dateModified'] == '2024-06-20T14:45:00'

    def test_set_dates_published(self):
        """Should set datePublished."""
        schema = ConcreteSchema('Thing')
        dt = datetime(2024, 6, 25)
        schema.set_dates(published=dt)
        assert schema.data['datePublished'] == '2024-06-25T00:00:00'

    def test_set_dates_all(self):
        """Should set all dates when provided."""
        schema = ConcreteSchema('Thing')
        created = datetime(2024, 1, 1)
        modified = datetime(2024, 6, 15)
        published = datetime(2024, 6, 20)

        schema.set_dates(created=created, modified=modified, published=published)

        assert 'dateCreated' in schema.data
        assert 'dateModified' in schema.data
        assert 'datePublished' in schema.data

    def test_set_dates_returns_self(self):
        """Should return self for method chaining."""
        schema = ConcreteSchema('Thing')
        result = schema.set_dates(created=datetime.now())
        assert result is schema


class TestSchemaOrgBaseRelationship:
    """Test add_relationship method."""

    def test_add_relationship_string_url(self):
        """Should add URL string relationship."""
        schema = ConcreteSchema('Thing')
        schema.add_relationship('isPartOf', 'https://example.com/collection')
        assert schema.data['isPartOf'] == 'https://example.com/collection'

    def test_add_relationship_schema_object(self):
        """Should add SchemaOrgBase object as dict."""
        parent = ConcreteSchema('Thing')
        related = ConcreteSchema('Collection')
        related.set_property('name', 'My Collection')

        parent.add_relationship('isPartOf', related)

        assert parent.data['isPartOf']['@type'] == 'Collection'
        assert parent.data['isPartOf']['name'] == 'My Collection'

    def test_add_relationship_returns_self(self):
        """Should return self for method chaining."""
        schema = ConcreteSchema('Thing')
        result = schema.add_relationship('isPartOf', 'https://example.com')
        assert result is schema


class TestSchemaOrgBaseOutput:
    """Test output methods."""

    def test_to_dict(self):
        """Should return dictionary representation."""
        schema = ConcreteSchema('Thing')
        schema.set_property('name', 'Test')

        result = schema.to_dict()

        assert isinstance(result, dict)
        assert result['@type'] == 'Thing'
        assert result['name'] == 'Test'

    def test_to_dict_returns_copy(self):
        """Should return a copy, not the original."""
        schema = ConcreteSchema('Thing')
        dict1 = schema.to_dict()
        dict1['modified'] = 'value'

        dict2 = schema.to_dict()
        assert 'modified' not in dict2

    def test_to_json_ld(self):
        """Should return JSON-LD string."""
        schema = ConcreteSchema('Thing')
        schema.set_property('name', 'Test')

        json_str = schema.to_json_ld()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed['@type'] == 'Thing'
        assert parsed['name'] == 'Test'

    def test_to_json_ld_indent(self):
        """Should respect indent parameter."""
        schema = ConcreteSchema('Thing')

        json_2 = schema.to_json_ld(indent=2)
        json_4 = schema.to_json_ld(indent=4)

        # More indentation = longer string
        assert len(json_4) > len(json_2)

    def test_to_json_ld_script(self):
        """Should return script tag with JSON-LD."""
        schema = ConcreteSchema('Thing')
        script = schema.to_json_ld_script()

        assert script.startswith('<script type="application/ld+json">')
        assert script.endswith('</script>')
        assert '"@type": "Thing"' in script


class TestSchemaOrgBaseValidation:
    """Test validation methods."""

    def test_validate_required_missing(self):
        """Should return list of missing required properties."""
        schema = ConcreteSchema('Thing')
        # Don't set 'name' which is required
        missing = schema.validate_required_properties()
        assert 'name' in missing

    def test_validate_required_present(self):
        """Should return empty list when all required present."""
        schema = ConcreteSchema('Thing')
        schema.set_property('name', 'Test')
        missing = schema.validate_required_properties()
        assert missing == []


class TestSchemaOrgBaseCompletionScore:
    """Test get_completion_score method."""

    def test_completion_score_all_required(self):
        """Should return 1.0 when all required properties present."""
        schema = ConcreteSchema('Thing')
        schema.set_property('name', 'Test')
        score = schema.get_completion_score()
        assert score == 1.0

    def test_completion_score_none_present(self):
        """Should return 0.0 when no required properties present."""
        schema = ConcreteSchema('Thing')
        score = schema.get_completion_score()
        assert score == 0.0

    def test_completion_score_recommended_count_half(self):
        """Recommended properties should count as 0.5."""
        schema = ConcreteSchema('Thing')
        schema.set_property('name', 'Test')  # Required
        schema.set_property('description', 'A test')  # Recommended

        # Score should be 1.0 (all required) + partial for recommended
        # But capped at 1.0
        score = schema.get_completion_score()
        assert score == 1.0


class TestSchemaOrgBaseStringMethods:
    """Test __str__ and __repr__ methods."""

    def test_str_returns_json_ld(self):
        """__str__ should return JSON-LD string."""
        schema = ConcreteSchema('Thing')
        str_repr = str(schema)
        assert '"@type": "Thing"' in str_repr

    def test_repr_format(self):
        """__repr__ should return class name and type."""
        schema = ConcreteSchema('Thing')
        repr_str = repr(schema)
        assert 'ConcreteSchema' in repr_str
        assert 'type=Thing' in repr_str


class TestMethodChaining:
    """Test that methods can be chained together."""

    def test_full_method_chain(self):
        """Should support full method chaining."""
        schema = ConcreteSchema('Article')

        result = (schema
            .set_property('name', 'Test Article')
            .add_person('author', 'John Doe')
            .add_organization('publisher', 'News Corp')
            .add_keywords(['news', 'article'])
            .set_dates(created=datetime.now())
            .set_identifier('ART-001')
        )

        assert result is schema
        assert schema.data['name'] == 'Test Article'
        assert schema.data['author']['name'] == 'John Doe'
        assert schema.data['publisher']['name'] == 'News Corp'

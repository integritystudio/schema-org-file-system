#!/usr/bin/env python3
"""
Integration tests for schema.org JSON-LD serialization.

Tests verify that all model classes properly serialize to schema.org format
with correct @context, @type, @id, and relationship properties.
"""

import json
import pytest
from datetime import datetime
from typing import Dict, Any

from storage.models import (
    File, Category, Company, Person, Location,
    FileStatus, Base
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


@pytest.fixture
def db_session() -> Session:
    """Create an in-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestFileSchemaOrg:
    """Tests for File.to_schema_org() serialization."""

    def test_file_basic_schema_org(self, db_session: Session):
        """Test basic File serialization to schema.org."""
        file = File(
            id="abc123def456",
            filename="document.pdf",
            original_path="/documents/document.pdf",
            mime_type="application/pdf",
            file_size=102400,
        )
        db_session.add(file)
        db_session.commit()

        schema_org = file.to_schema_org()

        # Verify structure
        assert schema_org["@context"] == "https://schema.org"
        assert schema_org["@type"] == "DigitalDocument"
        assert "@id" in schema_org
        assert schema_org["name"] == "document.pdf"
        assert schema_org["encodingFormat"] == "application/pdf"
        assert schema_org["contentSize"] == "102400"

    def test_file_image_schema_org(self, db_session: Session):
        """Test File serialization for ImageObject."""
        file = File(
            id="img123",
            filename="photo.png",
            original_path="/images/photo.png",
            mime_type="image/png",
            file_size=51200,
            image_width=1920,
            image_height=1080,
            has_faces=True,
            gps_latitude=40.7128,
            gps_longitude=-74.0060,
        )
        db_session.add(file)
        db_session.commit()

        schema_org = file.to_schema_org()

        # Verify image-specific properties
        assert schema_org["@type"] == "ImageObject"
        assert schema_org["width"] == 1920
        assert schema_org["height"] == 1080
        assert schema_org["hasFaces"] is True
        assert "contentLocation" in schema_org
        assert schema_org["contentLocation"]["@type"] == "Place"
        assert schema_org["contentLocation"]["geo"]["latitude"] == 40.7128

    def test_file_with_categories(self, db_session: Session):
        """Test File with category relationships in schema.org."""
        category = Category(
            name="Documents",
            canonical_id="cat-001",
            description="Important documents"
        )
        db_session.add(category)
        db_session.flush()

        file = File(
            id="file001",
            filename="contract.pdf",
            original_path="/docs/contract.pdf",
            mime_type="application/pdf",
        )
        file.categories.append(category)
        db_session.add(file)
        db_session.commit()

        schema_org = file.to_schema_org()

        # Verify category relationships
        assert "about" in schema_org
        assert len(schema_org["about"]) == 1
        assert schema_org["about"][0]["@type"] == "DefinedTerm"
        assert schema_org["about"][0]["name"] == "Documents"

    def test_file_with_mentions(self, db_session: Session):
        """Test File with company and person mentions."""
        company = Company(
            name="Acme Corp",
            canonical_id="acme-001",
            normalized_name="acme corp"
        )
        person = Person(
            name="John Doe",
            canonical_id="john-doe-001",
            normalized_name="john doe"
        )
        db_session.add_all([company, person])
        db_session.flush()

        file = File(
            id="file002",
            filename="report.pdf",
            original_path="/reports/report.pdf",
            mime_type="application/pdf",
        )
        file.companies.append(company)
        file.people.append(person)
        db_session.add(file)
        db_session.commit()

        schema_org = file.to_schema_org()

        # Verify mentions
        assert "mentions" in schema_org
        assert len(schema_org["mentions"]) == 2
        org_mention = next((m for m in schema_org["mentions"] if m["@type"] == "Organization"), None)
        person_mention = next((m for m in schema_org["mentions"] if m["@type"] == "Person"), None)
        assert org_mention is not None
        assert org_mention["name"] == "Acme Corp"
        assert person_mention is not None
        assert person_mention["name"] == "John Doe"

    def test_file_schema_type_from_mime(self):
        """Test MIME type to schema.org type mapping."""
        # Test various MIME types
        test_cases = [
            ("image/jpeg", "ImageObject"),
            ("image/png", "ImageObject"),
            ("video/mp4", "VideoObject"),
            ("audio/mpeg", "AudioObject"),
            ("application/pdf", "DigitalDocument"),
            ("text/html", "WebPage"),
            ("application/json", "SoftwareSourceCode"),
            ("text/plain", "DigitalDocument"),
            (None, "DigitalDocument"),
            ("unknown/type", "DigitalDocument"),
        ]

        for mime_type, expected_type in test_cases:
            result_type = File.get_schema_type_from_mime(mime_type)
            assert result_type == expected_type, f"Failed for MIME type {mime_type}"


class TestCategorySchemaOrg:
    """Tests for Category.to_schema_org() serialization."""

    def test_category_basic_schema_org(self, db_session: Session):
        """Test basic Category serialization."""
        category = Category(
            name="Legal Documents",
            canonical_id="legal-001",
            description="Legal and contract documents",
            icon="📋",
            color="#FF0000",
            level=0,
            full_path="Legal/Documents"
        )
        db_session.add(category)
        db_session.commit()

        schema_org = category.to_schema_org()

        # Verify structure
        assert schema_org["@context"] == "https://schema.org"
        assert schema_org["@type"] == "DefinedTerm"
        assert "@id" in schema_org
        assert schema_org["name"] == "Legal Documents"
        assert schema_org["definition"] == "Legal and contract documents"
        assert schema_org["identifier"] == "legal-documents"
        assert schema_org["icon"] == "📋"
        assert schema_org["color"] == "#FF0000"
        assert schema_org["inDefinedTermSet"]["@type"] == "DefinedTermSet"

    def test_category_hierarchy(self, db_session: Session):
        """Test Category hierarchy in schema.org."""
        parent = Category(
            name="Legal",
            canonical_id="legal-parent",
            level=0,
            full_path="Legal"
        )
        child = Category(
            name="Contracts",
            canonical_id="legal-contracts",
            level=1,
            full_path="Legal/Contracts",
            parent=parent
        )
        db_session.add_all([parent, child])
        db_session.commit()

        schema_org = child.to_schema_org()

        # Verify hierarchy
        assert "broader" in schema_org
        assert schema_org["broader"]["@type"] == "DefinedTerm"
        assert schema_org["broader"]["name"] == "Legal"

    def test_category_with_subcategories(self, db_session: Session):
        """Test Category with subcategories."""
        parent = Category(
            name="Media",
            canonical_id="media-parent",
            level=0,
            full_path="Media"
        )
        child1 = Category(
            name="Photos",
            canonical_id="media-photos",
            level=1,
            full_path="Media/Photos",
            parent=parent
        )
        child2 = Category(
            name="Videos",
            canonical_id="media-videos",
            level=1,
            full_path="Media/Videos",
            parent=parent
        )
        db_session.add_all([parent, child1, child2])
        db_session.commit()

        schema_org = parent.to_schema_org()

        # Verify subcategories
        assert "narrower" in schema_org
        assert len(schema_org["narrower"]) == 2
        names = [cat["name"] for cat in schema_org["narrower"]]
        assert "Photos" in names
        assert "Videos" in names


class TestCompanySchemaOrg:
    """Tests for Company.to_schema_org() serialization."""

    def test_company_basic_schema_org(self, db_session: Session):
        """Test basic Company serialization."""
        company = Company(
            name="TechCorp Inc",
            canonical_id="techcorp-001",
            normalized_name="techcorp inc",
            domain="techcorp.com",
            industry="Software",
            file_count=42,
            first_seen=datetime(2024, 1, 1),
            last_seen=datetime(2024, 3, 1),
        )
        db_session.add(company)
        db_session.commit()

        schema_org = company.to_schema_org()

        # Verify structure
        assert schema_org["@context"] == "https://schema.org"
        assert schema_org["@type"] == "Organization"
        assert "@id" in schema_org
        assert schema_org["name"] == "TechCorp Inc"
        assert schema_org["url"] == "https://techcorp.com"
        assert schema_org["knowsAbout"] == "Software"
        assert schema_org["mentionCount"] == 42
        assert "dateCreated" in schema_org
        assert "dateModified" in schema_org

    def test_company_url_formatting(self, db_session: Session):
        """Test Company URL formatting."""
        test_cases = [
            ("example.com", "https://example.com"),
            ("https://example.com", "https://example.com"),
            ("http://example.com", "http://example.com"),
        ]

        for domain, expected_url in test_cases:
            company = Company(
                name="TestCorp",
                canonical_id=f"test-{domain}",
                normalized_name="testcorp",
                domain=domain,
            )
            db_session.add(company)
            db_session.flush()

            schema_org = company.to_schema_org()
            assert schema_org["url"] == expected_url
            db_session.delete(company)
            db_session.flush()


class TestPersonSchemaOrg:
    """Tests for Person.to_schema_org() serialization."""

    def test_person_basic_schema_org(self, db_session: Session):
        """Test basic Person serialization."""
        person = Person(
            name="Jane Smith",
            canonical_id="jane-smith-001",
            normalized_name="jane smith",
            email="jane@example.com",
            role="Project Manager",
            file_count=15,
            first_seen=datetime(2024, 1, 15),
            last_seen=datetime(2024, 3, 10),
        )
        db_session.add(person)
        db_session.commit()

        schema_org = person.to_schema_org()

        # Verify structure
        assert schema_org["@context"] == "https://schema.org"
        assert schema_org["@type"] == "Person"
        assert "@id" in schema_org
        assert schema_org["name"] == "Jane Smith"
        assert schema_org["email"] == "jane@example.com"
        assert schema_org["jobTitle"] == "Project Manager"
        assert schema_org["mentionCount"] == 15

    def test_person_with_relationships(self, db_session: Session):
        """Test Person with relationships."""
        company = Company(
            name="TechCorp",
            canonical_id="techcorp-001",
            normalized_name="techcorp"
        )
        location = Location(
            name="San Francisco, CA",
            canonical_id="sf-001",
            city="San Francisco",
            state="CA",
            country="US"
        )
        db_session.add_all([company, location])
        db_session.flush()

        person = Person(
            name="John Developer",
            canonical_id="john-dev-001",
            normalized_name="john developer",
            email="john@techcorp.com",
            role="Senior Developer"
        )
        db_session.add(person)
        db_session.commit()

        schema_org = person.to_schema_org_with_relationships(
            company=company,
            location=location
        )

        # Verify relationships
        assert "worksFor" in schema_org
        assert schema_org["worksFor"]["@type"] == "Organization"
        assert schema_org["worksFor"]["name"] == "TechCorp"
        assert "workLocation" in schema_org
        assert schema_org["workLocation"]["@type"] == "Place"
        assert schema_org["workLocation"]["name"] == "San Francisco, CA"


class TestLocationSchemaOrg:
    """Tests for Location.to_schema_org() serialization."""

    def test_location_full_address(self, db_session: Session):
        """Test Location with full address."""
        location = Location(
            name="New York Office",
            canonical_id="ny-office-001",
            city="New York",
            state="NY",
            country="US",
            latitude=40.7128,
            longitude=-74.0060,
            file_count=30,
            created_at=datetime(2024, 1, 1),
        )
        db_session.add(location)
        db_session.commit()

        schema_org = location.to_schema_org()

        # Verify structure
        assert schema_org["@context"] == "https://schema.org"
        assert schema_org["@type"] == "Place"
        assert "@id" in schema_org
        assert schema_org["name"] == "New York Office"
        assert schema_org["address"]["@type"] == "PostalAddress"
        assert schema_org["address"]["addressLocality"] == "New York"
        assert schema_org["address"]["addressRegion"] == "NY"
        assert schema_org["address"]["addressCountry"] == "US"
        assert schema_org["geo"]["@type"] == "GeoCoordinates"
        assert schema_org["geo"]["latitude"] == 40.7128
        assert schema_org["geo"]["longitude"] == -74.0060
        assert schema_org["mentionCount"] == 30

    def test_location_city_only(self, db_session: Session):
        """Test Location with only city specified."""
        location = Location(
            name="London",
            canonical_id="london-001",
            city="London",
        )
        db_session.add(location)
        db_session.commit()

        schema_org = location.to_schema_org()

        # Should be City type
        assert schema_org["@type"] == "City"
        assert schema_org["address"]["addressLocality"] == "London"

    def test_location_country_only(self, db_session: Session):
        """Test Location with only country specified."""
        location = Location(
            name="France",
            canonical_id="france-001",
            country="FR",
        )
        db_session.add(location)
        db_session.commit()

        schema_org = location.to_schema_org()

        # Should be Country type
        assert schema_org["@type"] == "Country"
        assert schema_org["address"]["addressCountry"] == "FR"

    def test_location_with_geohash(self, db_session: Session):
        """Test Location with geohash."""
        location = Location(
            name="Test Location",
            canonical_id="test-001",
            latitude=51.5074,
            longitude=-0.1278,
            geohash="u33dc",
        )
        db_session.add(location)
        db_session.commit()

        schema_org = location.to_schema_org()

        # Verify geohash
        assert "geoHash" in schema_org
        assert schema_org["geoHash"] == "u33dc"


class TestJsonLdValidity:
    """Tests for JSON-LD structure validity."""

    def test_file_json_serializable(self, db_session: Session):
        """Test that File schema.org is JSON serializable."""
        file = File(
            id="test-001",
            filename="test.pdf",
            original_path="/test/test.pdf",
            mime_type="application/pdf",
        )
        db_session.add(file)
        db_session.commit()

        schema_org = file.to_schema_org()
        json_str = json.dumps(schema_org)
        parsed = json.loads(json_str)

        # Verify roundtrip
        assert parsed["name"] == "test.pdf"
        assert parsed["@type"] == "DigitalDocument"

    def test_all_entities_have_context_type_id(self, db_session: Session):
        """Test that all entities have @context, @type, and @id."""
        category = Category(name="Test", canonical_id="test-001")
        company = Company(name="Test", canonical_id="test-001", normalized_name="test")
        person = Person(name="Test", canonical_id="test-001", normalized_name="test")
        location = Location(name="Test", canonical_id="test-001")
        file = File(id="test-001", filename="test", original_path="/test")

        db_session.add_all([category, company, person, location, file])
        db_session.commit()

        for entity in [category, company, person, location, file]:
            schema_org = entity.to_schema_org()
            assert "@context" in schema_org, f"{entity.__class__.__name__} missing @context"
            assert "@type" in schema_org, f"{entity.__class__.__name__} missing @type"
            assert "@id" in schema_org, f"{entity.__class__.__name__} missing @id"

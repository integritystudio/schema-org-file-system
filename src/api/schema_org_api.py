#!/usr/bin/env python3
"""
Schema.org REST API endpoints.

Provides JSON-LD representations of entities in schema.org format.
Supports single entity retrieval and bulk export with filtering.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from storage.models import (
    File, Category, Company, Person, Location,
    Base
)
from storage.models import init_db, get_session
from api.schema_org_models import (
    FileSchemaOrg, CategorySchemaOrg, CompanySchemaOrg,
    PersonSchemaOrg, LocationSchemaOrg, BulkExportResponse,
    FileFilterParams, CategoryFilterParams, CompanyFilterParams,
    PersonFilterParams, LocationFilterParams, BulkExportParams,
    ErrorResponse
)


# Create FastAPI app
app = FastAPI(
    title="Schema.org API",
    description="JSON-LD representations of file system entities",
    version="1.0.0",
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    }
)


# Dependency for database session
def get_db() -> Session:
    """Get database session."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()


# File Endpoints
@app.get("/api/files/{file_id}/schema-org", response_model=Dict[str, Any])
async def get_file_schema_org(
    file_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get File as schema.org JSON-LD.

    Returns:
        File entity as schema.org JSON-LD with @context, @type, @id
    """
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_id} not found")

    return file.to_schema_org()


@app.get("/api/files/schema-org/bulk", response_model=List[Dict[str, Any]])
async def get_files_schema_org_bulk(
    params: FileFilterParams = Depends(),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get multiple Files as schema.org JSON-LD.

    Args:
        params: Pagination and filter parameters

    Returns:
        List of File entities as schema.org JSON-LD
    """
    query = db.query(File)

    if params.mime_type:
        query = query.filter(File.mime_type == params.mime_type)

    files = query.offset(params.skip).limit(params.limit).all()
    return [file.to_schema_org() for file in files]


# Category Endpoints
@app.get("/api/categories/{category_id}/schema-org", response_model=Dict[str, Any])
async def get_category_schema_org(
    category_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get Category as schema.org JSON-LD (DefinedTerm).

    Returns:
        Category entity as schema.org JSON-LD
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

    return category.to_schema_org()


@app.get("/api/categories/schema-org/bulk", response_model=List[Dict[str, Any]])
async def get_categories_schema_org_bulk(
    params: CategoryFilterParams = Depends(),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get multiple Categories as schema.org JSON-LD.

    Args:
        params: Pagination and filter parameters

    Returns:
        List of Category entities as schema.org JSON-LD
    """
    query = db.query(Category)

    if params.level is not None:
        query = query.filter(Category.level == params.level)

    categories = query.offset(params.skip).limit(params.limit).all()
    return [category.to_schema_org() for category in categories]


# Company Endpoints
@app.get("/api/companies/{company_id}/schema-org", response_model=Dict[str, Any])
async def get_company_schema_org(
    company_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get Company as schema.org JSON-LD (Organization).

    Returns:
        Company entity as schema.org JSON-LD
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    return company.to_schema_org()


@app.get("/api/companies/schema-org/by-name/{name}", response_model=Dict[str, Any])
async def get_company_by_name_schema_org(
    name: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get Company by name as schema.org JSON-LD.

    Args:
        name: Company name

    Returns:
        Company entity as schema.org JSON-LD
    """
    company = db.query(Company).filter(Company.normalized_name == name.lower().strip()).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{name}' not found")

    return company.to_schema_org()


@app.get("/api/companies/schema-org/bulk", response_model=List[Dict[str, Any]])
async def get_companies_schema_org_bulk(
    params: CompanyFilterParams = Depends(),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get multiple Companies as schema.org JSON-LD.

    Args:
        params: Pagination and filter parameters

    Returns:
        List of Company entities as schema.org JSON-LD
    """
    query = db.query(Company)

    if params.industry:
        query = query.filter(Company.industry == params.industry)

    companies = query.offset(params.skip).limit(params.limit).all()
    return [company.to_schema_org() for company in companies]


# Person Endpoints
@app.get("/api/people/{person_id}/schema-org", response_model=Dict[str, Any])
async def get_person_schema_org(
    person_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get Person as schema.org JSON-LD.

    Returns:
        Person entity as schema.org JSON-LD
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")

    return person.to_schema_org()


@app.get("/api/people/schema-org/by-name/{name}", response_model=Dict[str, Any])
async def get_person_by_name_schema_org(
    name: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get Person by name as schema.org JSON-LD.

    Args:
        name: Person name

    Returns:
        Person entity as schema.org JSON-LD
    """
    person = db.query(Person).filter(Person.normalized_name == name.lower().strip()).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person '{name}' not found")

    return person.to_schema_org()


@app.get("/api/people/schema-org/bulk", response_model=List[Dict[str, Any]])
async def get_people_schema_org_bulk(
    params: PersonFilterParams = Depends(),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get multiple People as schema.org JSON-LD.

    Args:
        params: Pagination and filter parameters

    Returns:
        List of Person entities as schema.org JSON-LD
    """
    query = db.query(Person)

    if params.role:
        query = query.filter(Person.role == params.role)

    people = query.offset(params.skip).limit(params.limit).all()
    return [person.to_schema_org() for person in people]


# Location Endpoints
@app.get("/api/locations/{location_id}/schema-org", response_model=Dict[str, Any])
async def get_location_schema_org(
    location_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get Location as schema.org JSON-LD (Place).

    Returns:
        Location entity as schema.org JSON-LD
    """
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

    return location.to_schema_org()


@app.get("/api/locations/schema-org/by-name/{name}", response_model=Dict[str, Any])
async def get_location_by_name_schema_org(
    name: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get Location by name as schema.org JSON-LD.

    Args:
        name: Location name

    Returns:
        Location entity as schema.org JSON-LD
    """
    location = db.query(Location).filter(Location.name == name).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"Location '{name}' not found")

    return location.to_schema_org()


@app.get("/api/locations/schema-org/bulk", response_model=List[Dict[str, Any]])
async def get_locations_schema_org_bulk(
    params: LocationFilterParams = Depends(),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get multiple Locations as schema.org JSON-LD.

    Args:
        params: Pagination and filter parameters

    Returns:
        List of Location entities as schema.org JSON-LD
    """
    query = db.query(Location)

    if params.country:
        query = query.filter(Location.country == params.country)

    locations = query.offset(params.skip).limit(params.limit).all()
    return [location.to_schema_org() for location in locations]


# Bulk Export Endpoint
@app.get("/api/schema-org/export", response_model=BulkExportResponse)
async def export_all_entities_schema_org(
    params: BulkExportParams = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export all entities as schema.org JSON-LD.

    Args:
        params: Export parameters (entity_types)

    Returns:
        Dictionary with entity type keys containing arrays of schema.org objects
    """
    export = {}
    entity_types_list = [t.strip().lower() for t in params.entity_types.split(",")]

    if "all" in entity_types_list or "file" in entity_types_list:
        files = db.query(File).all()
        export["files"] = [f.to_schema_org() for f in files]

    if "all" in entity_types_list or "category" in entity_types_list:
        categories = db.query(Category).all()
        export["categories"] = [c.to_schema_org() for c in categories]

    if "all" in entity_types_list or "company" in entity_types_list:
        companies = db.query(Company).all()
        export["companies"] = [c.to_schema_org() for c in companies]

    if "all" in entity_types_list or "person" in entity_types_list:
        people = db.query(Person).all()
        export["people"] = [p.to_schema_org() for p in people]

    if "all" in entity_types_list or "location" in entity_types_list:
        locations = db.query(Location).all()
        export["locations"] = [l.to_schema_org() for l in locations]

    return export


# Health Check
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

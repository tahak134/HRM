# tests/conftest.py
import os
import asyncio
import pytest
from httpx import AsyncClient
from app.main import app
from app.config import settings
from app.core.security import create_access_token

# import models to pass to init_db
from app.models.employee import Employee, EmergencyContact, EmploymentHistory, JobDetails
from app.models.performance import Goal, GoalDependency, GoalAssignment, PerformanceReview, Feedback, DevelopmentPlan
from app.models.documents import Document, DocumentVersion
from app.models.audit import AuditLog
from app.core import mongo_client

# tests/conftest.py or directly in test files

EMP_PAYLOAD = {
    "first_name": "John",
    "last_name": "Doe",
    "middle_name": "A",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "date_of_birth": "1990-01-01T00:00:00",
    "department": "engineering",    
    "position": "Software Engineer",
    "job_title": "Backend Developer",
    "hire_date": "2023-01-01T00:00:00",
    "employment_type": "full-time",

    # EmployeeCreate-specific fields
    "address": "123 Main St",
    "city": "Karachi",
    "state": "Sindh",
    "country": "Pakistan",
    "postal_code": "74000",
    "manager_id": None,
    "skills": ["Python", "FastAPI"],
    "certifications": ["AWS Certified Developer"]
}

@pytest.fixture(scope="function", autouse=True)
async def init_db():
    """Initialize Mongo + Beanie for all models."""
    document_models = [
        Employee, EmergencyContact, EmploymentHistory, JobDetails,
        Goal, GoalDependency, GoalAssignment, PerformanceReview, Feedback, DevelopmentPlan,
        Document, DocumentVersion, AuditLog,
    ]
    settings.database_name = os.getenv("TEST_MONGODB_DB", "epm_test_db")
    await mongo_client.connect_to_mongo(document_models)
    yield
    # cleanup (optional: drop db after tests)
    if mongo_client.client:
        mongo_client.client.drop_database(settings.database_name)
        mongo_client.client.close()

@pytest.fixture
async def client(init_db):
    """Async test client bound to the initialized app."""
    settings.access_token_expire_minutes = 60
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def token_headers():
    """Yield an `AsyncClient` for making test requests to the FastAPI app.

    The client is properly configured with the test app and a base URL of
    "http://testserver". The client is properly cleaned up after the test

    # create a token for a test user with roles
    is finished.
    """
    token = create_access_token(subject="TESTUSER", roles=["admin", "hr", "manager"])

    return {"Authorization": f"Bearer {token}"}

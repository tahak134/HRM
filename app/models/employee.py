from beanie import Document, Indexed, Link
from pydantic import Field, EmailStr
from datetime import datetime, date
from typing import Optional, List, Annotated
from enum import Enum
import uuid

def _id(prefix: str):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

class JobDetails(Document):  
    job_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("JOB"))
    employee_id: Annotated[str, Indexed()] = Field(...)
    title: Optional[str] = None
    department: Optional[str] = None
    manager_id: Optional[str] = None
    start_date: Optional[date] = None
    location: Optional[str] = None

    class Settings:
        name = "job_details"

class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"

class Department(str, Enum):
    ENGINEERING = "engineering"
    SALES = "sales"
    MARKETING = "marketing"
    HR = "hr"
    FINANCE = "finance"
    OPERATIONS = "operations"
    PRODUCT = "product"

class EmergencyContact(Document):
    employee_id: str
    name: str
    relationship: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    is_primary: bool = False
    
    class Settings:
        name = "emergency_contacts"
        indexes = [
            "employee_id"
        ]

class EmploymentHistory(Document):
    employee_id: str
    company_name: str
    position: str
    start_date: datetime
    end_date: Optional[datetime] = None
    responsibilities: List[str] = []
    achievements: List[str] = []
    reason_for_leaving: Optional[str] = None
    
    class Settings:
        name = "employment_history"
        indexes = [
            "employee_id"
        ]

class Employee(Document):
    # Basic Information
    employee_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("EMP"))
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Annotated[EmailStr, Indexed(unique=True)] = Field(...)
    phone: str
    date_of_birth: datetime
    hashed_password: str  
    
    # Job Details
    department: Department
    role: str = Field(default="employee")
    position: str
    job_title: str
    hire_date: datetime
    employment_type: str  # full-time, part-time, contract
    status: Optional[str] = Field(default="active")
    
    # Organizational Structure
    manager_id: Optional[str] = None
    team_members: List[str] = []
    
    # Personal Details
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    nationality: Optional[str] = None
    
    # Professional Details
    skills: List[str] = []
    certifications: List[str] = []
    education: List[dict] = []  # {degree, institution, year}
    
    # System Fields
    photo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Compensation (encrypted/sensitive)
    salary: Optional[float] = None
    bonus_eligible: bool = False
    
    class Settings:
        name = "employees"
        indexes = [
            "employee_id",
            "email",
            "department",
            "status",
            "manager_id",
            [("department", 1), ("status", 1)]
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@company.com",
                "phone": "+1234567890",
                "department": "engineering",
                "position": "Senior Software Engineer",
                "status": "active"
            }
        }
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models.employee import Employee, EmployeeStatus, Department
from app.schemas.common import MongoModel

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: EmailStr
    phone: str
    date_of_birth: datetime
    department: Department
    position: str
    job_title: str
    hire_date: datetime
    employment_type: str
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    address: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    password: str             # raw pw for signup
    role: str = "employee"
    address: str
    city: str
    state: str
    country: str
    postal_code: Optional[str] = None
    manager_id: Optional[str] = None
    skills: List[str] = []
    certifications: List[str] = []

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[Department] = None
    position: Optional[str] = None
    job_title: Optional[str] = None
    status: Optional[EmployeeStatus] = None
    manager_id: Optional[str] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    role: Optional[str] = None

class EmployeeResponse(MongoModel, EmployeeBase):
    role: str
    status: EmployeeStatus
    created_at: datetime
    updated_at: datetime
    photo_url: Optional[str] = None
    team_members: List[str] = []

    @classmethod
    def from_mongo(cls, emp: Employee):
        data = emp.dict()
        data["id"] = str(emp.id)   # force id into str
        return cls.model_validate(data)

class EmployeeSearch(BaseModel):
    department: Optional[Department] = None
    status: Optional[EmployeeStatus] = None
    manager_id: Optional[str] = None
    skills: Optional[List[str]] = None
    hire_date_from: Optional[datetime] = None
    hire_date_to: Optional[datetime] = None
    search_text: Optional[str] = None

class BulkUpdateRequest(BaseModel):
    employee_ids: List[str]
    updates: EmployeeUpdate


class EmergencyContactCreate(BaseModel):
    name: str
    relationship: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    is_primary: bool = False

class EmploymentHistoryCreate(BaseModel):
    company_name: str
    position: str
    start_date: datetime
    end_date: Optional[datetime] = None
    responsibilities: List[str] = []
    achievements: List[str] = []
    reason_for_leaving: Optional[str] = None
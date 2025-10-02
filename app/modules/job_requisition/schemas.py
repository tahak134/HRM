from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobRequisitionSummary(BaseModel):
    id: str
    title: str
    vacant_positions: int
    employment_type: str
    status: str


class JobRequisitionCreate(BaseModel):
    title: str
    vacant_positions: int
    employment_type: str
    job_location: str
    expected_joining_date: datetime
    responsibilities: str
    required_qualification: str
    required_experience: str
    skills: List[str]

class InitiatorOut(BaseModel):
    name: Optional[str]
    designation: Optional[str]
    department: Optional[str]
    emp_id: Optional[str]
    email: Optional[str]

class SalaryRange(BaseModel):
    minSalary: Optional[int]
    maxSalary: Optional[int]
    miscExpense: Optional[int]

class JobRequisitionOut(BaseModel):
    id: str
    title: str
    department: str
    designation: str
    requested_by: str
    date_requested: datetime
    vacant_positions: Optional[int]
    employment_type: Optional[str]
    job_location: Optional[str]
    expected_joining_date: datetime
    responsibilities: Optional[str]
    required_qualification: Optional[str]
    required_experience: Optional[str]
    skills: Optional[List[str]]
    salary_range: Optional[SalaryRange]
    status: Optional[str]
    approved_by: Optional[str]
    reviewed_by: Optional[str]
    date_of_review: Optional[datetime]
    date_of_approval: Optional[datetime]
    remarks: Optional[str]
    initiator: Optional[InitiatorOut] = None

class SalaryRangeOut(BaseModel):
    minSalary: Optional[int]
    maxSalary: Optional[int]
    miscExpense: Optional[int]


class ReviewerOut(BaseModel):
    name: Optional[str]
    designation: Optional[str]
    department: Optional[str]
    emp_id: Optional[str]
    email: Optional[str]


class BudgetOut(BaseModel):
    id: Optional[str]  # will map to "_id" converted to str
    jobTitle: Optional[str]
    minSalary: Optional[int]
    maxSalary: Optional[int]
    department: Optional[str]
    miscExpense: Optional[int]
    lastUpdated: Optional[datetime]


class JobRequisitionOutV2(BaseModel):
    id: str
    title: str
    department: str
    designation: str
    requested_by: str
    date_requested: datetime
    vacant_positions: Optional[int]
    employment_type: Optional[str]
    job_location: Optional[str]
    expected_joining_date: datetime
    responsibilities: Optional[str]
    required_qualification: Optional[str]
    required_experience: Optional[str]
    skills: Optional[List[str]]
    salary_range: Optional[SalaryRangeOut]
    status: Optional[str]
    approved_by: Optional[str]
    reviewed_by: Optional[str]
    date_of_review: Optional[datetime]
    date_of_approval: Optional[datetime]
    remarks: Optional[str]
    initiator: Optional[dict] = None
    reviewer: Optional[ReviewerOut] = None
    budget: Optional[BudgetOut] = None


class JobRequisitionUpdate(BaseModel):
    title: Optional[str] = None
    vacant_positions: Optional[int] = None
    employment_type: Optional[str] = None
    job_location: Optional[str] = None
    expected_joining_date: Optional[str] = None
    responsibilities: Optional[str] = None
    required_qualification: Optional[str] = None
    required_experience: Optional[str] = None
    skills: Optional[List[str]] = None
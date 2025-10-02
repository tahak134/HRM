# app/models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str           # e.g. "admin", "hr", "manager", "employee"
    department: str

class UserInDB(BaseModel):
    id: Optional[str]  # MongoDB ObjectId as string
    name: str
    email: EmailStr
    hashed_password: str
    role: str
    department: str

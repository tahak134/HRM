# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from datetime import datetime

from app.core.security import (
    verify_password, get_password_hash, create_access_token
)
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()   # expects "Authorization: Bearer <token>"

# ------------------------
# Request/Response Models
# ------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    auth_token: str
    token_type: str = "bearer"

# ------------------------
# Login
# ------------------------
@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await Employee.find_one(Employee.email == payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_data = {"sub": str(user.id), "role": user.role, "department": user.department }
    auth_token = create_access_token(token_data)
    return {"auth_token": auth_token, "token_type": "bearer"}

# ------------------------
# Signup (restricted to Admin/HR)
# ------------------------
@router.post("/signup")
async def signup(
    user: EmployeeCreate,
    current=Depends(lambda: RoleChecker(["admin", "hr"]))
):
    existing = await Employee.find_one(Employee.email == user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    emp = Employee(
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        email=user.email,
        phone=user.phone,
        date_of_birth=user.date_of_birth,
        department=user.department,
        position=user.position,
        job_title=user.job_title,
        hire_date=user.hire_date,
        employment_type=user.employment_type,
        address=user.address,
        city=user.city,
        state=user.state,
        country=user.country,
        postal_code=user.postal_code,
        manager_id=user.manager_id,
        skills=user.skills or [],
        certifications=user.certifications or [],
        hashed_password=get_password_hash(user.password),
        role=user.role,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await emp.insert()
    return {"id": str(emp.id), "email": emp.email, "role": emp.role}

# ------------------------
# Current User
# ------------------------
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await Employee.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_active_user(current_user: Employee = Depends(get_current_user)):
    # Here you could check additional flags like `is_active`
    return current_user

# ------------------------
# Role-based dependency
# ------------------------
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: Employee = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="You don't have enough permissions")
        return user

# ------------------------
# Example protected route
# ------------------------
@router.get("/users")
async def list_users(_: Employee = Depends(RoleChecker(["admin", "hr"]))):
    users = []
    async for emp in Employee.find_all():
        users.append({
            "id": str(emp.id),
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "role": emp.role,
            "department": emp.department,
        })
    return users

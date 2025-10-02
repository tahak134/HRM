from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.models.employee import Employee
from app.core.security import oauth2_scheme, get_password_hash, require_roles
from datetime import datetime
from pydantic import BaseModel
router = APIRouter(prefix="/api/v1/employees", tags=["employees"])

class SetPasswordRequest(BaseModel):
    password: str

@router.post("/{id}/set-password", status_code=200)
async def set_employee_password(        
    id: str,
    request: SetPasswordRequest,
    # PROTECT THIS ENDPOINT: Ensure only admins/hr can use it.
    # This line might be different depending on your auth setup.
    current_user: dict = Depends(require_roles(["admin", "hr"])) 
):
    """Allows an admin to set an initial password for an employee."""
    employee = await Employee.get(id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Hash the new password and save it to the database
    employee.hashed_password = get_password_hash(request.password)
    await employee.save()

    return {"message": f"Password for employee {employee.email} has been set successfully."}

@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    skip: int = 0,
    limit: int = 10,
    department: Optional[str] = None,
    position: Optional[str] = None,
    city: Optional[str] = None,
    skills: Optional[str] = None,  # comma-separated
    hire_date_from: Optional[datetime] = None,
    hire_date_to: Optional[datetime] = None,
    search_text: Optional[str] = None,
):
    # Build a query dict
    query = {}
    if department:
        query["department"] = department
    if position:
        query["position"] = position
    if city:
        query["city"] = city
    if skills:
        # match any of the provided skills
        skill_list = [s.strip() for s in skills.split(",") if s.strip()]
        if skill_list:
            query["skills"] = {"$in": skill_list}
    if hire_date_from or hire_date_to:
        date_query = {}
        if hire_date_from:
            date_query["$gte"] = hire_date_from
        if hire_date_to:
            date_query["$lte"] = hire_date_to
        if date_query:
            query["hire_date"] = date_query
    if search_text:
        # simple text search on first_name, last_name, position, email
        query["$or"] = [
            {"first_name": {"$regex": search_text, "$options": "i"}},
            {"last_name": {"$regex": search_text, "$options": "i"}},
            {"position": {"$regex": search_text, "$options": "i"}},
            {"email": {"$regex": search_text, "$options": "i"}},
        ]

    docs_cursor = Employee.find(query).skip(skip).limit(limit)
    results = await docs_cursor.to_list()
    return [EmployeeResponse.from_mongo(emp) for emp in results]

@router.get("/{id}", response_model=EmployeeResponse)
async def get_employee(id: str):
    try:
        emp = await Employee.get(id)
    except Exception:
        emp = None
    if not emp:
        raise HTTPException(404, "Employee not found")
    return EmployeeResponse.from_mongo(emp)

@router.post("/", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreate, token: str = Depends(oauth2_scheme)):
    emp = Employee(**employee.dict(), created_by="admin")
    await emp.insert()
    return EmployeeResponse.from_mongo(emp)

@router.put("/{id}", response_model=EmployeeResponse)
async def update_employee(id: str, employee: EmployeeUpdate):
    emp = await Employee.get(id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    await emp.set(employee.dict(exclude_unset=True))
    return EmployeeResponse.from_mongo(emp)

@router.delete("/{id}")
async def delete_employee(id: str):
    emp = await Employee.get(id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    await emp.delete()
    return {"message": "Employee deleted"}

@router.post("/{employee_id}/profile-picture", response_model=EmployeeResponse)
async def upload_profile_picture(employee_id: str, file: UploadFile = File(...)):
    emp = await Employee.get(employee_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    
    path = f"uploads/{employee_id}_{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    
    emp.photo_url = path
    await emp.save()
    return EmployeeResponse.from_mongo(emp)

@router.get("/stats")
async def employee_stats():
    total = await Employee.count()
    active = await Employee.find({"status": "active"}).count()
    return {"total": total, "active": active}

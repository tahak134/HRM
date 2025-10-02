from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from typing import List, Optional
from app.schemas.document import DocumentResponse, DocumentUpload, DocumentUpdate
from app.models.documents import Document, DocumentStatus
from app.models.employee import Employee
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.security import get_current_user
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    department: Optional[str] = Query(None),
    employeeId: Optional[str] = Query(None), 
    current_user: dict = Depends(get_current_user)
):
    query = {}

    # Apply filters based on role
    if current_user['role'] == 'admin' or current_user['role'] == 'hr':
        if department:
            query['department'] = department
    elif current_user['role'] == 'manager':
        query['department'] = current_user['department']
    elif current_user['role'] == 'employee':
        query['employee_id'] = current_user['user_id'] 

    docs = await Document.find(query).to_list()
    return [DocumentResponse.from_mongo(d) for d in docs]

@router.get("/{id}", response_model=DocumentResponse)
async def get_document(id: str):
    doc = await Document.get(id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return DocumentResponse.from_mongo(doc)

@router.post("/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    employee_id: str = Form(...),
    name: str = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    description: str = Form(None),
    tags: str = Form(None),
    is_confidential: bool = Form(False),
    expires_at: str = Form(None),
    uploaded_by: str = Form("admin")
):
    
    employee = await Employee.get(employee_id) # Use .get() to fetch by _id
    if not employee:
        raise HTTPException(status_code=404, detail="Employee to associate with document not found")

    path = f"uploads/{file.filename}"
    contents = await file.read()
    with open(path, "wb") as f:
        f.write(contents)
    
    file_size = len(contents)

    auto_tags = [type, category]
    if file.filename.lower().endswith((".pdf", ".doc", ".docx", ".txt")):
        ext = file.filename.split(".")[-1]
        auto_tags.append(ext)
    if file.filename.lower().endswith((".jpg", ".png")):
        auto_tags.append("image")

    doc = Document(
        employee_id=employee_id,
        name=name,
        type=type,
        category=category,
        description=description,
        tags=(tags.split(",") if tags else []) + auto_tags,
        is_confidential=is_confidential,
        version=1,
        file_name=file.filename,
        file_size=file_size,
        file_path=path,
        department=employee.department,
        mime_type=file.content_type,
        status = DocumentStatus.PENDING,
        expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
        uploaded_by=uploaded_by
    )
    await doc.insert()
    return DocumentResponse.from_mongo(doc)

@router.put("/{id}", response_model=DocumentResponse)
async def update_document(id: str, document: DocumentUpdate):
    doc = await Document.get(id)
    if not doc:
        raise HTTPException(404, "Document not found")
    await doc.set(document.dict(exclude_unset=True))
    updated = await Document.get(id)
    return DocumentResponse.from_mongo(updated)

@router.delete("/{id}")
async def delete_document(id: str):
    doc = await Document.get(id)
    if not doc:
        raise HTTPException(404, "Document not found")
    await doc.delete()
    return {"message": "Document deleted"}

@router.post("/{id}/approve", response_model=DocumentResponse)
async def approve_document(id: str, approver_id: str = Form(...)):
    doc = await Document.get(id)
    if not doc:
        raise HTTPException(404, "Document not found")
    doc.approved = True
    doc.approved_by = approver_id
    doc.approval_date = datetime.utcnow()
    doc.status = "active"
    await doc.save()
    return DocumentResponse.from_mongo(doc)

@router.post("/{id}/new-version", response_model=DocumentResponse)
async def new_version(id: str, file: UploadFile = File(...)):
    old_doc = await Document.get(id)
    if not old_doc:
        raise HTTPException(404, "Document not found")

    path = f"uploads/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    new_doc = Document(
        employee_id=old_doc.employee_id,
        name=old_doc.name,
        type=old_doc.type,
        category=old_doc.category,
        description=old_doc.description,
        tags=old_doc.tags,
        is_confidential=old_doc.is_confidential,
        file_name=file.filename,
        file_size=file.spool_max_size,
        status="pending_approval",
        version=old_doc.version + 1
    )
    await new_doc.insert()
    return DocumentResponse.from_mongo(new_doc)

@router.on_event("startup")
async def check_expired_docs():
    scheduler = AsyncIOScheduler()

    async def expire_docs():
        now = datetime.utcnow()
        expired = await Document.find(Document.expires_at < now, Document.status == "active").to_list()
        for doc in expired:
            doc.status = "expired"
            await doc.save()
            # TODO: send email/notification

    scheduler.add_job(expire_docs, "interval", hours=24)
    scheduler.start()

@router.get("/{id}/download")
async def download_document(id: str):
    doc = await Document.get(id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return {"file_path": doc.file_name}

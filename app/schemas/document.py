from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.documents import DocumentType, DocumentStatus, Document
from app.schemas.common import MongoModel

class DocumentUpload(BaseModel):
    name: str
    type: DocumentType
    category: str
    description: Optional[str] = None
    tags: List[str] = []
    expiry_date: Optional[datetime] = None
    is_confidential: bool = False

class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    expiry_date: Optional[datetime] = None

class DocumentApproval(BaseModel):
    status: DocumentStatus
    rejection_reason: Optional[str] = None

class DocumentResponse(MongoModel):
    # The 'id' field is correctly inherited from MongoModel, so we don't redefine it.
    employee_id: str
    name: str
    type: str
    category: str
    description: Optional[str]
    tags: List[str]
    is_confidential: bool
    version: int
    file_name: str
    file_path: str
    mime_type: str
    file_size: int
    expiry_date: Optional[datetime]
    status: DocumentStatus
    uploaded_by: str
    uploaded_at: datetime

    @classmethod
    def from_mongo(cls, doc: Document):
        data = doc.dict()
        data["id"] = str(doc.id)  # force ObjectId → str
        return cls.model_validate(data)


class DocumentVersionResponse(BaseModel):
    version_id: str
    document_id: str
    version_number: int
    change_summary: str
    changed_by: str
    changed_at: datetime

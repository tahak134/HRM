from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime, time
from typing import Optional, List, Dict, Annotated
from enum import Enum
import uuid

def _id(prefix: str):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

class DocumentType(str, Enum):
    CONTRACT = "contract"
    CERTIFICATE = "certificate"
    ID_PROOF = "id_proof"
    EDUCATION = "education"
    POLICY = "policy"
    AGREEMENT = "agreement"
    OTHER = "other"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Document(Document):
    document_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("DOC"))
    document_group_id: Annotated[str, Indexed()] = Field(default_factory=lambda: _id("DOCG"))
    employee_id: str
    
    # Document Info
    name: str
    type: str
    category: str
    description: Optional[str] = None
    department: Optional[str] = None
    
    # File Details
    file_path: str
    file_name: str
    file_size: int  # in bytes
    mime_type: str
    
    # Metadata
    tags: List[str] = []
    keywords: List[str] = []  # For search
    
    # Status & Approval
    status: DocumentStatus = DocumentStatus.PENDING
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Expiration
    expiry_date: Optional[datetime] = None
    reminder_sent: bool = False
    reminder_date: Optional[datetime] = None
    
    # Version Control
    version: int = 1
    is_latest: bool = True
    parent_document_id: Optional[str] = None
    
    # Security
    is_confidential: bool = False
    access_restricted: bool = False
    allowed_viewers: List[str] = []  # Employee IDs
    
    # System Fields
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "documents"
        indexes = [
            "document_id",
            "document_group_id",
            "employee_id",
            "is_latest",
            [("document_group_id", 1)],
            [("employee_id", 1)]
        ]

class DocumentVersion(Document):
    version_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("DV"))
    document_id: Annotated[str, Indexed()] = Field(...)
    document_group_id: Annotated[str, Indexed()] = Field(...)
    version_number: int
    change_summary: Optional[str] = None
    changed_by: Optional[str] = None
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    file_path: str
    file_name: str
    file_size: int
    mime_type: Optional[str] = None

    class Settings:
        name = "document_versions"
        indexes = [
            "version_id",
            [("document_id", 1)],
            [("document_group_id", 1)],
            [("version_number", 1)]
        ]
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any, Annotated, List
import uuid

def _id(prefix: str):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

class AuditLog(Document):
    audit_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("AUD"))
    
    # Action Details
    action: str  # create, update, delete, view, download
    entity_type: str  # employee, goal, review, document, etc.
    entity_id: str
    
    # User Information
    performed_by: str  # Employee ID
    performed_by_name: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Change Details
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changed_fields: List[str] = []
    
    # Additional Context
    reason: Optional[str] = None
    comments: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Session Info
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    class Settings:
        name = "audit_logs"
        indexes = [
            "audit_id",
            "entity_type",
            "entity_id",
            "performed_by",
            "timestamp",
            [("entity_type", 1), ("entity_id", 1), ("timestamp", -1)]
        ]
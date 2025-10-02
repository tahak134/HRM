# app/utils/audit_logger.py
from typing import Optional, Dict, Any, List
from app.models.audit import AuditLog 
import uuid
from datetime import datetime

async def create_audit_log(
    action: str,
    entity_type: str,
    entity_id: str,
    performed_by: str,
    performed_by_name: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    changed_fields: Optional[List[str]] = None,
    reason: Optional[str] = None,
    session=None
):
    """
    Create an audit log entry. Optionally pass Motor session to include in transaction.
    """
    audit_id = f"AUD{str(uuid.uuid4())[:8].upper()}"
    data = AuditLog(
        audit_id=audit_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        performed_by=performed_by,
        performed_by_name=performed_by_name or performed_by,
        old_values=old_values,
        new_values=new_values,
        changed_fields=changed_fields or [],
        reason=reason,
        timestamp=datetime.utcnow()
    )
    # Save optionally within a MongoDB session if provided
    if session:
        await data.insert(session=session)
    else:
        await data.insert()
    return data

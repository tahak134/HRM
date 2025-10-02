# tests/test_documents.py
import pytest
import io
from tests.conftest import EMP_PAYLOAD

@pytest.mark.asyncio
async def test_upload_document(client, token_headers):
    # create employee
    r = await client.post(
        "/api/v1/employees/",
        json={**EMP_PAYLOAD, "email": "docu@example.com"},
        headers=token_headers
    )
    emp_id = r.json()["employee_id"]

    file_content = b"%PDF-1.4 test pdf content"  # simple fake pdf header
    files = {
        "file": ("test_doc.pdf", io.BytesIO(file_content), "application/pdf")
    }
    data = {
        "employee_id": emp_id,
        "name": "Employment Contract",
        "type": "policy",         
        "category": "hr",       
        "description": "Signed employment contract",
        "tags": ["contract", "hr"],
        "is_confidential": False
    }
    res = await client.post(
        "/api/v1/documents/upload",
        data=data,
        files=files,
        headers=token_headers
    )
    assert res.status_code in (200, 201)
    body = res.json()
    assert "document_id" in body
    assert "employee_id" in body
    assert body["employee_id"] == emp_id

@pytest.mark.asyncio
@pytest.mark.skip(reason="Document auto-tagging not implemented yet")
async def test_document_auto_tagging(client, token_headers):
    # placeholder for future feature
    pass

@pytest.mark.asyncio
@pytest.mark.skip(reason="Virus scanning not implemented; integrate clamav or similar and then enable")
async def test_virus_scan_rejection(client, token_headers):
    # simulate a malicious file and expect rejection after virus scan
    pass

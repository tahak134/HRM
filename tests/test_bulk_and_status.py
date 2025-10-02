# tests/test_bulk_and_status.py
import pytest
from app.core.security import create_access_token
from tests.conftest import EMP_PAYLOAD

@pytest.mark.asyncio
@pytest.mark.skip(reason="Bulk update endpoint not implemented yet")
async def test_bulk_update_employees(client, token_headers):
    # This test will call a hypothetical endpoint /api/v1/employees/bulk_update
    payload = {"employee_ids": ["EMP1","EMP2"], "changes": {"status":"on_leave"}}
    res = await client.post("/api/v1/employees/bulk_update", json=payload, headers=token_headers)
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_status_management(client, token_headers):
    r = await client.post("/api/v1/employees/", json=EMP_PAYLOAD, headers=token_headers)
    eid = r.json()["employee_id"]
    # set status to on_leave
    res = await client.patch(f"/api/v1/employees/{eid}", json={"status":"on_leave"}, headers=token_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "on_leave"
    # set status to terminated (requires hr role)
    # generate hr token
    hr_token = create_access_token(subject="HRTEST", roles=["hr"])

    headers = {"Authorization": f"Bearer {hr_token}"}
    res2 = await client.delete(f"/api/v1/employees/{eid}", headers=headers)
    assert res2.status_code == 200

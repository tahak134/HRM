# tests/test_employees.py
import pytest
from httpx import AsyncClient
from tests.conftest import EMP_PAYLOAD

@pytest.mark.asyncio
async def test_create_employee(client: AsyncClient, token_headers):
    res = await client.post("/api/v1/employees/", json={**EMP_PAYLOAD, "email": "unique123@example.com"}, headers=token_headers)
    assert res.status_code == 200 or res.status_code == 201
    body = res.json()
    assert body["email"] == EMP_PAYLOAD["email"]
    assert "_id" in body
    # save id for next tests via attribute on response for test sequence (not ideal in parallel)
    pytest.employee_id = body["_id"]

@pytest.mark.asyncio
async def test_get_employee(client: AsyncClient, token_headers):
    emp_id = getattr(pytest, "employee_id", None)
    assert emp_id is not None, "employee_id fixture missing (run test_create_employee first)"
    res = await client.get(f"/api/v1/employees/{emp_id}", headers=token_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["_id"] == emp_id

@pytest.mark.asyncio
async def test_update_employee(client: AsyncClient, token_headers):
    emp_id = getattr(pytest, "employee_id", None)
    payload = {"phone": "+199999999"}
    res = await client.patch(f"/api/v1/employees/{emp_id}", json=payload, headers=token_headers)
    assert res.status_code == 200
    assert res.json()["phone"] == payload["phone"]

@pytest.mark.asyncio
async def test_list_employees_search_and_pagination(client: AsyncClient, token_headers):
    # create a few employees
    for i in range(3):
        await client.post("/api/v1/employees/", json={
            "first_name": f"Bulk{i}",
            "last_name": "Tester",
            "email": f"bulk{i}.tester@example.com"
        }, headers=token_headers)
    res = await client.get("/api/v1/employees/?skip=0&limit=2", headers=token_headers)
    assert res.status_code == 200
    lst = res.json()
    assert isinstance(lst, list)

@pytest.mark.asyncio
async def test_delete_employee(client: AsyncClient, token_headers):
    emp_id = getattr(pytest, "employee_id", None)
    res = await client.delete(f"/api/v1/employees/{emp_id}", headers=token_headers)
    assert res.status_code == 200
    # verify deleted
    res2 = await client.get(f"/api/v1/employees/{emp_id}", headers=token_headers)
    assert res2.status_code == 404

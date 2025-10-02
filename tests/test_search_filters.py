import pytest
from tests.conftest import EMP_PAYLOAD


@pytest.mark.asyncio
async def test_search_by_team_and_filters(client, token_headers):
    # create employees
    for i in range(2):
        payload = {**EMP_PAYLOAD, "email": f"search{i}@ex.com", "first_name": f"S{i}"}
        res = await client.post("/api/v1/employees/", json=payload, headers=token_headers)
        assert res.status_code in (200, 201)

    res = await client.get("/api/v1/employees/?department=engineering", headers=token_headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert any(emp["department"] == "engineering" for emp in data)

# tests/test_performance.py
import pytest
from tests.conftest import EMP_PAYLOAD

@pytest.mark.asyncio
async def test_create_goal_and_dependency_and_cycle(client, token_headers):
    # create two employees
    r1 = await client.post("/api/v1/employees/", json={**EMP_PAYLOAD, "email": "g1@example.com"}, headers=token_headers)
    e1 = r1.json()["id"]

    r2 = await client.post("/api/v1/employees/", json={**EMP_PAYLOAD, "email": "g2@example.com"}, headers=token_headers)
    e2 = r2.json()["id"]

    # create a goal
    goal_payload = {
        "title": "Finish project",
        "description": "Deliver backend",
        "category": "performance",
        "type": "individual",
        "priority": "high",
        "start_date": "2025-01-01T00:00:00",
        "due_date": "2025-12-31T00:00:00",
        "employee_id": e1
    }
    res = await client.post("/api/v1/performance/goals/", json=goal_payload, headers=token_headers)
    assert res.status_code in (200, 201)
    goal = res.json()

    # create a dependency
    dep_payload = {"from_goal_id": goal["goal_id"], "to_goal_id": goal["goal_id"], "dep_type": "blocks"}
    res = await client.post("/api/v1/performance/dependencies/", json=dep_payload, headers=token_headers)
    assert res.status_code in (200, 201)

    # create a cycle
    cycle_payload = {"name": "Q1 2024", "description": "Quarterly review"}
    res = await client.post("/api/v1/performance/cycles/", json=cycle_payload, headers=token_headers)
    assert res.status_code in (200, 201)

@pytest.mark.asyncio
async def test_assign_goal_and_review_feedback(client, token_headers):
    # create employee
    r = await client.post("/api/v1/employees/", json={**EMP_PAYLOAD, "email": "ab@example.com"}, headers=token_headers)
    emp_id = r.json()["employee_id"]

    # create goal
    g = await client.post(
        "/api/v1/performance/goals",
        json={
            "title": "Assign Test",
            "description": "Goal for testing assignment",
            "category": "performance",
            "type": "individual",
            "priority": "high",
            "start_date": "2025-01-01T00:00:00",
            "due_date": "2025-12-31T00:00:00",
            "employee_id": emp_id,
            "owner_employee_id": emp_id
        },
        headers=token_headers
    )
    assert g.status_code in (200, 201)
    gid = g.json()["goal_id"]

    # assign employee to goal
    assign = await client.post(
        "/api/v1/performance/goals/assign",
        json={"goal_id": gid, "assignee_id": emp_id, "role": "owner"},
        headers=token_headers
    )
    assert assign.status_code == 200
    assert "assignment_id" in assign.json()

    review_payload = {
    "employee_id": emp_id,
    "reviewer_id": emp_id,
    "review_type": "annual",   
    "review_period_start": "2024-01-01T00:00:00",
    "review_period_end": "2024-12-31T00:00:00"
}

    # create review
    rev = await client.post(
        "/api/v1/performance/reviews",
        json=review_payload,
        headers=token_headers
    )
    assert rev.status_code in (200, 201)

    # create feedback
    fb = await client.post(
        "/api/v1/performance/feedback",
        json={
            "employee_id": emp_id,
            "feedback_type": "peer",
            "content": "Great job, keep it up!",
            "rating": 5,
            "categories": ["teamwork"]
        },
        headers=token_headers
    )
    assert fb.status_code in (200, 201)
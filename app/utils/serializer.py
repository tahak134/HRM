# app/utils/serializers.py
from typing import Any, Dict, List
from datetime import datetime
from enum import Enum

def _to_str(v):
    try:
        return str(v)
    except Exception:
        return None

def _date_to_iso(d: datetime):
    if not d:
        return None
    try:
        return d.isoformat()
    except Exception:
        return None

def serialize_goal(goal) -> Dict[str, Any]:
    """
    Convert a Beanie Goal document to a JSON-safe dict the frontend expects.
    Adjust the keys here to whatever your frontend requires.
    """
    # id resolution (priority: id -> _id -> goal_id)
    id_val = getattr(goal, "id", None) or getattr(goal, "_id", None) or getattr(goal, "goal_id", None)
    # employee id mapping: frontend expects `employee_id`
    employee_id = getattr(goal, "owner_employee_id", None) or getattr(goal, "employee_id", None)
    # status may be an Enum
    status = getattr(goal, "status", None)
    if isinstance(status, Enum):
        status = status.value

    # assignees: convert embedded GoalAssignee models to dicts
    assignees = []
    for a in getattr(goal, "assignees", []) or []:
        try:
            assignee = {
                "assignee_id": _to_str(getattr(a, "assignee_id", None)),
                "role": getattr(a, "role").value if hasattr(getattr(a, "role", None), "value") else getattr(a, "role", None),
                "allocation_percent": getattr(a, "allocation_percent", None),
                "start_date": _date_to_iso(getattr(a, "start_date", None)),
                "end_date": _date_to_iso(getattr(a, "end_date", None)),
                "assigned_at": _date_to_iso(getattr(a, "assigned_at", None)),
                "assigned_by": getattr(a, "assigned_by", None),
            }
        except Exception:
            # fallback: if a is already a dict
            if isinstance(a, dict):
                assignee = a
            else:
                assignee = {"assignee_id": _to_str(a)}
        assignees.append(assignee)

    # map fields your frontend expects (add/remove as needed)
    out = {
        "id": _to_str(id_val),
        "goal_id": getattr(goal, "goal_id", None),
        "employee_id": employee_id,
        "owner_employee_id": getattr(goal, "owner_employee_id", None),
        "title": getattr(goal, "title", None),
        "description": getattr(goal, "description", None),
        "category": getattr(goal, "category", None),
        "type": getattr(goal, "type", None),
        "priority": getattr(goal, "priority", None),
        "start_date": _date_to_iso(getattr(goal, "start_date", None)),
        "due_date": _date_to_iso(getattr(goal, "due_date", None)),
        "target_date": _date_to_iso(getattr(goal, "due_date", None)),  # frontend expects target_date sometimes
        "completed_date": _date_to_iso(getattr(goal, "completed_date", None)),
        "status": status,
        "progress_percentage": float(getattr(goal, "progress_percentage", 0.0) or 0.0),
        "milestones": getattr(goal, "milestones", []) or [],
        "target_value": getattr(goal, "target_value", None),
        "current_value": getattr(goal, "current_value", None),
        "unit_of_measurement": getattr(goal, "unit_of_measurement", None),
        "parent_goal_id": getattr(goal, "parent_goal_id", None),
        "dependent_goals": getattr(goal, "dependent_goals", []) or [],
        "aligned_with": getattr(goal, "aligned_with", []) or [],
        "aligned_to": getattr(goal, "aligned_to", None) or (getattr(goal, "aligned_with", []) and ",".join(getattr(goal, "aligned_with", []))),
        "assignees": assignees,
        "achievement_probability": getattr(goal, "achievement_probability", None),
        "risk_factors": getattr(goal, "risk_factors", []) or [],
        "recommendations": getattr(goal, "recommendations", []) or [],
        "created_at": _date_to_iso(getattr(goal, "created_at", None)),
        "updated_at": _date_to_iso(getattr(goal, "updated_at", None)),
        "created_by": getattr(goal, "created_by", None),
        "updated_by": getattr(goal, "updated_by", None),
    }
    return out

from datetime import datetime

def job_requisition_doc(data: dict, user: dict):
    return {
        "title": data["title"],
        "department": user["department"],
        "designation": user["designation"],
        "requested_by": user["emp_id"],
        "date_requested": datetime.utcnow(),
        "vacant_positions": data["vacant_positions"],
        "employment_type": data["employment_type"],
        "job_location": data["job_location"],
        "expected_joining_date": data["expected_joining_date"],
        "responsibilities": data["responsibilities"],
        "required_qualification": data["required_qualification"],
        "required_experience": data["required_experience"],
        "skills": data["skills"],
        "salary_range": None,
        "status": "Pending Review",  # initial status
        "approved_by": None,
        "reviewed_by": None,
        "date_of_review": None,
        "date_of_approval": None,
        "remarks": None,
    }

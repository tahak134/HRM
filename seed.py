# seed.py
"""
Seed script (fixed: single event loop + timezone-aware datetimes)
Run:
    python seed.py
Set MONGO_URI env var if needed, default is mongodb://localhost:27017/emp_db
"""

import os
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Adjust imports to your code layout
from app.models.employee import Employee
from app.models.documents import Document
from app.models.performance import Goal, PerformanceReview, Feedback

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/emp_db")


def clean_payload(d: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None / empty-string values to reduce validation noise"""
    out = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        out[k] = v
    return out


async def seed_all():
    inserted = {"employees": 0, "documents": 0, "goals": 0, "reviews": 0, "feedback": 0}
    errors = 0

    now = datetime.now(timezone.utc)

    # ---------- EMPLOYEES ----------
    employees = [
        {
            "employee_id": "EMP0001",
            "first_name": "Sarah",
            "last_name": "Chen",
            "email": "sarah.chen@example.com",
            "phone": "+1-415-555-0101",
            "date_of_birth": datetime(1990, 5, 12, tzinfo=timezone.utc),
            "department": "engineering",
            "position": "IC4",
            "job_title": "Senior Software Engineer",
            "hire_date": datetime(2018, 2, 15, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": "EMP0016",
            "address": "123 Market St",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94103",
            "skills": ["python", "react", "system-design"],
            "certifications": ["aws-solutions-architect"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0002",
            "first_name": "Elena",
            "last_name": "Rodriguez",
            "email": "elena.rodriguez@example.com",
            "phone": "+1-415-555-0102",
            "date_of_birth": datetime(1991, 9, 3, tzinfo=timezone.utc),
            "department": "product",
            "position": "IC3",
            "job_title": "Senior UX Designer",
            "hire_date": datetime(2019, 7, 1, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": "EMP0004",
            "address": "Remote",
            "city": "Remote",
            "state": "Remote",
            "country": "USA",
            "postal_code": "00000",
            "skills": ["ux", "research", "figma"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0003",
            "first_name": "David",
            "last_name": "Kim",
            "email": "david.kim@example.com",
            "phone": "+1-415-555-0103",
            "date_of_birth": datetime(1992, 11, 10, tzinfo=timezone.utc),
            "department": "engineering",
            "position": "IC2",
            "job_title": "Data Analyst",
            "hire_date": datetime(2020, 1, 20, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": "EMP0016",
            "address": "456 3rd Ave",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10001",
            "skills": ["sql", "python", "tableau"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0004",
            "first_name": "Marcus",
            "last_name": "Johnson",
            "email": "marcus.johnson@example.com",
            "phone": "+1-415-555-0104",
            "date_of_birth": datetime(1987, 6, 22, tzinfo=timezone.utc),
            "department": "product",
            "position": "Manager",
            "job_title": "Product Manager",
            "hire_date": datetime(2016, 3, 10, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": "EMP0001",
            "address": "100 Executive Dr",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94105",
            "skills": ["product", "analytics"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0005",
            "first_name": "Aisha",
            "last_name": "Rahman",
            "email": "aisha.rahman@example.com",
            "phone": "+1-415-555-0105",
            "date_of_birth": datetime(1993, 8, 2, tzinfo=timezone.utc),
            "department": "engineering",
            "position": "IC2",
            "job_title": "Software Engineer",
            "hire_date": datetime(2021, 6, 1, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": "EMP0001",
            "address": "22 Van Ness Ave",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94109",
            "skills": ["nodejs", "typescript"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0006",
            "first_name": "Omar",
            "last_name": "Ali",
            "email": "omar.ali@example.com",
            "phone": "+1-415-555-0106",
            "date_of_birth": datetime(1989, 12, 5, tzinfo=timezone.utc),
            "department": "marketing",
            "position": "IC3",
            "job_title": "Growth Marketer",
            "hire_date": datetime(2017, 9, 15, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": "EMP0009",
            "address": "12 Mission St",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94107",
            "skills": ["growth", "analytics"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0007",
            "first_name": "Priya",
            "last_name": "Desai",
            "email": "priya.desai@example.com",
            "phone": "+1-415-555-0107",
            "date_of_birth": datetime(1994, 3, 14, tzinfo=timezone.utc),
            "department": "sales",
            "position": "IC2",
            "job_title": "Account Executive",
            "hire_date": datetime(2020, 4, 5, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": "EMP0009",
            "address": "77 Howard St",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94103",
            "skills": ["sales", "crm"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0008",
            "first_name": "Liu",
            "last_name": "Wang",
            "email": "liu.wang@example.com",
            "phone": "+1-415-555-0108",
            "date_of_birth": datetime(1990, 1, 25, tzinfo=timezone.utc),
            "department": "engineering",
            "position": "IC3",
            "job_title": "Staff Engineer",
            "hire_date": datetime(2015, 11, 2, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": "EMP0001",
            "address": "500 Embarcadero",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94107",
            "skills": ["backend", "scalability"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0009",
            "first_name": "Jon",
            "last_name": "Smith",
            "email": "jon.smith@example.com",
            "phone": "+1-415-555-0109",
            "date_of_birth": datetime(1985, 4, 20, tzinfo=timezone.utc),
            "department": "marketing",
            "position": "Manager",
            "job_title": "Head of Marketing",
            "hire_date": datetime(2014, 8, 10, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": None,
            "address": "250 Market St",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94105",
            "skills": ["branding", "growth"],
            "created_by": "EMP0010",
        },
        {
            "employee_id": "EMP0010",
            "first_name": "Maya",
            "last_name": "Garcia",
            "email": "maya.garcia@example.com",
            "phone": "+1-415-555-0110",
            "date_of_birth": datetime(1995, 7, 19, tzinfo=timezone.utc),
            "department": "hr",
            "position": "Manager",
            "job_title": "HR Business Partner",
            "hire_date": datetime(2018, 10, 1, tzinfo=timezone.utc),
            "employment_type": "full_time",
            "status": "active",
            "manager_id": None,
            "address": "789 Market St",
            "city": "San Francisco",
            "state": "CA",
            "country": "USA",
            "postal_code": "94103",
            "skills": ["talent", "onboarding"],
            "created_by": "EMP0010",
        },
    ]

    # quickly add EMP0011..EMP0020
    for i in range(11, 21):
        emp_id = f"EMP{str(i).zfill(4)}"
        employees.append(
            {
                "employee_id": emp_id,
                "first_name": f"First{i}",
                "last_name": f"Last{i}",
                "email": f"user{i}@example.com",
                "phone": f"+1-415-555-{100+i}",
                "date_of_birth": datetime(1990, 1, (i % 28) + 1, tzinfo=timezone.utc),
                "department": ["engineering", "sales", "marketing", "finance", "operations", "product"][i % 6],
                "position": "IC2",
                "job_title": "Contributor",
                "hire_date": datetime(2021, 1, 1, tzinfo=timezone.utc),
                "employment_type": "full_time",
                "status": "active",
                "manager_id": "EMP0010" if i % 4 == 0 else "EMP0004",
                "address": f"{i} Test St",
                "city": "San Francisco",
                "state": "CA",
                "country": "USA",
                "postal_code": "94103",
                "skills": [],
                "created_by": "EMP0010",
            }
        )

    for payload in employees:
        p = clean_payload(payload)
        try:
            inst = Employee(**p)
            await inst.insert()
            inserted["employees"] += 1
            print("Inserted employee", p.get("employee_id"))
        except Exception as e:
            errors += 1
            print("Failed to insert employee", p.get("employee_id"), "-", repr(e))

    # ---------- DOCUMENTS ----------
    documents = [
        {
            "document_id": "DOC001",
            "employee_id": "EMP0001",
            "name": "Employment Contract - Sarah",
            "type": "contract",
            "category": "employment",
            "description": "Signed employment contract",
            "file_path": "uploads/EMP0001_contract.pdf",
            "file_name": "EMP0001_contract.pdf",
            "file_size": 120000,
            "mime_type": "application/pdf",
            "tags": ["contract"],
            "status": "approved",
            "uploaded_by": "EMP0010",
            "uploaded_at": now,
        },
        {
            "document_id": "DOC002",
            "employee_id": "EMP0003",
            "name": "Analytics Certificate",
            "type": "certificate",
            "category": "certification",
            "file_path": "uploads/EMP0003_cert.pdf",
            "file_name": "EMP0003_cert.pdf",
            "file_size": 40000,
            "mime_type": "application/pdf",
            "tags": ["certificate"],
            "status": "approved",
            "uploaded_by": "EMP0003",
            "uploaded_at": now,
        },
        {
            "document_id": "DOC003",
            "employee_id": "EMP0005",
            "name": "ID Proof",
            "type": "id_proof",
            "category": "id",
            "file_path": "uploads/EMP0005_id.pdf",
            "file_name": "EMP0005_id.pdf",
            "file_size": 15000,
            "mime_type": "application/pdf",
            "tags": ["id"],
            "status": "approved",
            "uploaded_by": "EMP0005",
            "uploaded_at": now,
        },
    ]

    for payload in documents:
        p = clean_payload(payload)
        try:
            inst = Document(**p)
            await inst.insert()
            inserted["documents"] += 1
            print("Inserted document", p.get("document_id"))
        except Exception as e:
            errors += 1
            print("Failed to insert document", p.get("document_id"), "-", repr(e))

    # ---------- GOALS ----------
    goals = [
        {
            "goal_id": "GOL001",
            "owner_employee_id": "EMP0004",
            "title": "Increase onboarding completion to 80%",
            "description": "Improve onboarding flows to achieve 80% completion",
            "category": "product",
            "type": "team",
            "priority": "high",
            "start_date": now - timedelta(days=20),
            "due_date": now + timedelta(days=40),
            "progress_percentage": 45.0,
            "status": "in_progress",
            "milestones": [
                {"title": "MVP onboarding", "due_date": (now - timedelta(days=1)), "completed": True, "notes": "launched"},
                {"title": "A/B test flows", "due_date": (now + timedelta(days=15)), "completed": False},
            ],
            "assignees": [
                {"assignee_id": "EMP0004", "role": "owner", "assigned_at": now - timedelta(days=20)},
                {"assignee_id": "EMP0002", "role": "contributor", "assigned_at": now - timedelta(days=20)},
            ],
            "created_by": "EMP0010",
        },
        {
            "goal_id": "GOL002",
            "owner_employee_id": "EMP0014",
            "title": "Reduce page load time to <1.2s",
            "description": "Performance improvements for core app endpoints",
            "category": "engineering",
            "type": "team",
            "priority": "high",
            "start_date": now - timedelta(days=10),
            "due_date": now + timedelta(days=30),
            "progress_percentage": 30.0,
            "status": "in_progress",
            "assignees": [
                {"assignee_id": "EMP0011", "role": "contributor", "assigned_at": now - timedelta(days=10)},
                {"assignee_id": "EMP0012", "role": "contributor", "assigned_at": now - timedelta(days=10)},
            ],
            "created_by": "EMP0010",
        },
        {
            "goal_id": "GOL003",
            "owner_employee_id": "EMP0008",
            "title": "Improve NPS by 10 points",
            "description": "Cross-functional improvements",
            "category": "marketing",
            "type": "company",
            "priority": "medium",
            "start_date": now,
            "due_date": now + timedelta(days=60),
            "progress_percentage": 20.0,
            "status": "not_started",
            "assignees": [
                {"assignee_id": "EMP0007", "role": "contributor", "assigned_at": now},
                {"assignee_id": "EMP0019", "role": "contributor", "assigned_at": now},
            ],
            "created_by": "EMP0010",
        },
    ]

    for payload in goals:
        p = clean_payload(payload)
        try:
            inst = Goal(**p)
            await inst.insert()
            inserted["goals"] += 1
            print("Inserted goal", p.get("goal_id"))
        except Exception as e:
            errors += 1
            print("Failed to insert goal", p.get("goal_id"), "-", repr(e))

    # ---------- PERFORMANCE REVIEWS ----------
    reviews = [
        {
            "review_id": "REV2024Q1_EMP0001",
            "employee_id": "EMP0001",
            "reviewer_id": "EMP0016",
            "review_type": "quarterly",
            "review_period_start": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "review_period_end": datetime(2024, 3, 31, tzinfo=timezone.utc),
            "overall_rating": 4.5,
            "ratings": {"communication": 4.5, "delivery": 4.7},
            "strengths": ["architecture", "mentorship"],
            "areas_for_improvement": ["documentation"],
            "achievements": ["Launched payments feature"],
            "goals_achieved": ["GOL001"],
            "status": "finalized",
            "created_at": now - timedelta(days=15),
        },
        {
            "review_id": "REV2024Q1_EMP0002",
            "employee_id": "EMP0002",
            "reviewer_id": "EMP0004",
            "review_type": "quarterly",
            "review_period_start": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "review_period_end": datetime(2024, 3, 31, tzinfo=timezone.utc),
            "overall_rating": 4.7,
            "ratings": {"design": 4.8, "collaboration": 4.6},
            "strengths": ["design leadership"],
            "areas_for_improvement": ["prioritization"],
            "achievements": ["Redesigned onboarding flow"],
            "status": "finalized",
            "created_at": now - timedelta(days=12),
        },
    ]

    for payload in reviews:
        p = clean_payload(payload)
        try:
            inst = PerformanceReview(**p)
            await inst.insert()
            inserted["reviews"] += 1
            print("Inserted review", p.get("review_id"))
        except Exception as e:
            errors += 1
            print("Failed to insert review", p.get("review_id"), "-", repr(e))

    # ---------- FEEDBACK ----------
    feedbacks = [
        {
            "feedback_id": "FBD001",
            "receiver_id": "EMP0001",
            "giver_id": "EMP0002",
            "feedback_type": "peer",
            "content": "Great leadership on the payments rollout.",
            "rating": 5.0,
            "categories": ["leadership"],
            "is_anonymous": False,
            "sentiment_score": 0.95,
            "sentiment": "positive",
            "created_at": now - timedelta(days=10),
        },
        {
            "feedback_id": "FBD002",
            "receiver_id": "EMP0003",
            "giver_id": "EMP0001",
            "feedback_type": "manager",
            "content": "Excellent analytics work on Q1 report.",
            "rating": 4.0,
            "categories": ["analytics"],
            "is_anonymous": False,
            "sentiment_score": 0.8,
            "sentiment": "positive",
            "created_at": now - timedelta(days=9),
        },
        {
            "feedback_id": "FBD003",
            "receiver_id": "EMP0007",
            "giver_id": "EMP0008",
            "feedback_type": "peer",
            "content": "Thanks for helping close that deal!",
            "rating": 4.0,
            "categories": ["sales"],
            "is_anonymous": False,
            "sentiment_score": 0.7,
            "sentiment": "positive",
            "created_at": now - timedelta(days=5),
        },
        {
            "feedback_id": "FBD004",
            "receiver_id": "EMP0002",
            "giver_id": "EMP0010",  # model requires giver_id; flagged as anonymous
            "feedback_type": "peer",
            "content": "Anonymous recognition for mentoring.",
            "rating": None,
            "categories": ["coaching"],
            "is_anonymous": True,
            "sentiment_score": 0.9,
            "sentiment": "positive",
            "created_at": now - timedelta(days=3),
        },
    ]

    for payload in feedbacks:
        p = clean_payload(payload)
        try:
            inst = Feedback(**p)
            await inst.insert()
            inserted["feedback"] += 1
            print("Inserted feedback", p.get("feedback_id"))
        except Exception as e:
            errors += 1
            print("Failed to insert feedback", p.get("feedback_id"), "-", repr(e))

    print("Seeding finished. Summary:", inserted)
    print("Encountered errors:", errors)


async def main():
    client = AsyncIOMotorClient(MONGO_URI)
    try:
        # Initialize Beanie with models (Database will be client.get_default_database())
        await init_beanie(
            database=client.get_default_database(),
            document_models=[Employee, Document, Goal, PerformanceReview, Feedback],
        )
        print("Initialized Beanie with models:", [m.__name__ for m in (Employee, Document, Goal, PerformanceReview, Feedback)])
        # Run seeder
        await seed_all()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())

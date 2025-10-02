from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.job_requisition.schemas import (
    JobRequisitionCreate,
    JobRequisitionOut,
    JobRequisitionUpdate,
    JobRequisitionSummary,
    JobRequisitionOutV2,
)
from app.modules.job_requisition.models import job_requisition_doc as JobRequisition
from app.core.security import get_current_user
from bson import ObjectId
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import google.generativeai as genai
import os

router = APIRouter(prefix="/api/v1/job-requisition", tags=["Job Requisition"])

# ------------------------------------------------------
# Helpers
# ------------------------------------------------------

def normalize_doc(doc: JobRequisition) -> dict:
    """Convert Beanie Document → dict with string id"""
    if not doc:
        return None
    data = doc.dict()
    data["id"] = str(doc.id)
    return data


# ------------------------------------------------------
# Endpoints
# ------------------------------------------------------

@router.post("/", response_model=JobRequisitionOut)
async def create_job_requisition(
    req: JobRequisitionCreate,
    current_user: dict = Depends(get_current_user),
):
    """Requester (any employee) raises a job requisition request"""
    user_id = str(current_user.get("_id") or current_user.get("id"))

    doc = JobRequisition(
        **req.dict(),
        department=current_user.get("department"),
        designation=current_user.get("designation"),
        requested_by=current_user.get("emp_id"),
        date_requested=datetime.utcnow(),
        status="Pending Review",
    )
    await doc.insert()
    return normalize_doc(doc)


@router.put("/{req_id}", response_model=JobRequisitionOut)
async def update_job_requisition(
    req_id: str,
    req: JobRequisitionUpdate,
    current_user: dict = Depends(get_current_user),
):
    doc = await JobRequisition.get(req_id)
    if not doc:
        raise HTTPException(404, "Requisition not found")

    await doc.set({**req.dict(exclude_unset=True), "updated_at": datetime.utcnow()})
    return normalize_doc(doc)


@router.get("/my-requests", response_model=list[JobRequisitionSummary])
async def get_my_requisitions(current_user: dict = Depends(get_current_user)):
    emp_id = current_user.get("emp_id")
    docs = await JobRequisition.find({"requested_by": emp_id}).sort("-date_requested").to_list()
    return [normalize_doc(d) for d in docs]


@router.get("/request/{req_id}", response_model=JobRequisitionOut)
async def get_my_requisition(req_id: str):
    doc = await JobRequisition.get(req_id)
    if not doc:
        raise HTTPException(404, "Requisition not found")
    return normalize_doc(doc)


@router.delete("/{req_id}")
async def withdraw_requisition(req_id: str, current_user: dict = Depends(get_current_user)):
    doc = await JobRequisition.get(req_id)
    if not doc:
        raise HTTPException(404, "Requisition not found")

    if doc.requested_by != current_user.get("emp_id"):
        raise HTTPException(403, "Not allowed to withdraw this requisition")
    if doc.status != "Pending Review":
        raise HTTPException(400, "Can only withdraw requisitions in Pending Review")

    await doc.set({"status": "Withdrawn"})
    return {"message": "Requisition withdrawn successfully"}


# HOD Review
class ReviewRequest(BaseModel):
    action: str  # "accept" or "reject"
    remarks: Optional[str] = None


@router.put("/{req_id}/review")
async def review_job_requisition(req_id: str, review: ReviewRequest, current_user: dict = Depends(get_current_user)):
    doc = await JobRequisition.get(req_id)
    if not doc:
        raise HTTPException(404, "Requisition not found")

    if (current_user.get("designation") or "").lower() != "hod":
        raise HTTPException(403, "Only HODs can review requisitions")

    update = {"reviewed_by": current_user.get("emp_id"), "date_of_review": datetime.utcnow()}

    if review.action == "reject":
        if not review.remarks:
            raise HTTPException(400, "Remarks required when rejecting")
        update.update({"status": "Rejected", "remarks": review.remarks})
    elif review.action == "accept":
        update.update({"status": "Pending Approval"})
    else:
        raise HTTPException(400, "Invalid action")

    await doc.set(update)
    return normalize_doc(doc)


# ------------------------------------------------------
# Gemini Integration (unchanged, still raw insert)
# ------------------------------------------------------

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class JDResponse(BaseModel):
    job_request_id: str
    job_description: str


@router.post("/{req_id}/generate", response_model=JDResponse)
async def generate_job_description(req_id: str, current_user: dict = Depends(get_current_user)):
    doc = await JobRequisition.get(req_id)
    if not doc:
        raise HTTPException(404, "Requisition not found")

    if doc.status != "Approved":
        raise HTTPException(400, "Only Approved requisitions can generate JD")

    job_data = {
        "Title": doc.title,
        "Vacant Positions": doc.vacant_positions,
        "Employment Type": doc.employment_type,
        "Job Location": doc.job_location,
        "Responsibilities": doc.responsibilities,
        "Qualification": doc.required_qualification,
        "Experience": doc.required_experience,
        "Skills": ", ".join(doc.skills or []),
    }

    prompt = f"""Generate a professional job description:
    {job_data}
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)
        jd_text = response.text
    except Exception as e:
        raise HTTPException(500, f"Gemini API error: {str(e)}")

    # Keep job_descriptions as raw if you don’t have a Beanie model yet
    from app.database import db
    await db["job_descriptions"].insert_one({
        "job_request_id": str(doc.id),
        "job_description": jd_text,
        "generated_by": current_user.get("emp_id"),
        "date_generated": datetime.utcnow(),
    })

    return {"job_request_id": str(doc.id), "job_description": jd_text}

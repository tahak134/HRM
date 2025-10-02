import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas.performance import PerformanceReviewCreate, PerformanceReviewUpdate, PerformanceReviewResponse, FeedbackResponse
from app.models.performance import PerformanceReview, Feedback
from app.models.employee import Employee
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/performance", tags=["performance"])

@router.get("/reviews", response_model=List[PerformanceReviewResponse])
async def get_performance_reviews(
    department: Optional[str] = Query(None),
    employeeId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    query = {}
    user_role = current_user.get("role")

    if user_role == 'manager':
        # Managers see reviews only for their department
        query["department"] = current_user.get("department")
    elif user_role == 'employee':
        # Employees see only their own reviews
        query["employee_id"] = current_user.get("user_id")
    elif user_role in ['admin', 'hr'] and department:
        # Admins/HR can filter by department if they choose to
        query["department"] = department
    # If admin/hr don't provide a department, the query is empty and they get all reviews.

    perf = await PerformanceReview.find(query).to_list()
    return [PerformanceReviewResponse.from_mongo(fb) for fb in perf]

@router.get("/feedback", response_model=List[FeedbackResponse])
async def get_all_feedback(
    department: Optional[str] = Query(None),
    employeeId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Fetches feedback with role-based filtering."""
    # This assumes your 'Feedback' model has 'department' and 'employee_id' fields
    query = {}
    user_role = current_user.get("role")
    
    if user_role == 'manager':
        query["department"] = current_user.get("department")
    elif user_role == 'employee':
        query["employee_id"] = current_user.get("user_id")
    elif user_role in ['admin', 'hr'] and department:
        query["department"] = department
    
    fb = await Feedback.find(query).to_list()
    return [FeedbackResponse.from_mongo(fb) for fb in fb]

@router.get("/reviews/{id}", response_model=PerformanceReviewResponse)
async def get_single_review(id: str):
    """Gets a single performance review by its ID."""
    review = await PerformanceReview.get(id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return PerformanceReviewResponse.from_mongo(review)

@router.post("/reviews", response_model=PerformanceReviewResponse)
async def create_performance_review(review: PerformanceReviewCreate, current_user=Depends(get_current_user)):
    # Fetch employee to get department
    employee = await Employee.find_one(Employee.employee_id == review.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    review_doc = PerformanceReview(
        **review.dict(),
        department=employee.department,   # auto-populate department
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await review_doc.insert()
    return review_doc


@router.put("/reviews/{id}", response_model=PerformanceReviewResponse)
async def update_performance_review(id: str, review: PerformanceReviewUpdate):
    r = await PerformanceReview.get(id)
    if not r:
        raise HTTPException(404, "Review not found")
    await r.set(review.dict(exclude_unset=True))
    return r

@router.delete("/reviews/{id}")
async def delete_performance_review(id: str):
    r = await PerformanceReview.get(id)
    if not r:
        raise HTTPException(404, "Review not found")
    await r.delete()
    return {"message": "Review deleted"}

@router.get("/metrics/{employee_id}")
async def get_performance_metrics(employee_id: str):
    # Placeholder: calculate metrics from reviews
    reviews = await PerformanceReview.find({"employee_id": employee_id}).to_list()
    avg_rating = sum(r.overall_rating or 0 for r in reviews) / max(len(reviews), 1)
    return {"employee_id": employee_id, "average_rating": avg_rating}

@router.get("/stats")
async def get_performance_stats():
    total = await PerformanceReview.count()
    completed = await PerformanceReview.find({"status": "completed"}).count()
    return {"total_reviews": total, "completed_reviews": completed}

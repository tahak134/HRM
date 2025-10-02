from fastapi import APIRouter, HTTPException
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from app.ai.trainer import train_model
from app.ai.predictor import predict_employee, predict_goal_probability
from app.api.v1.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/insights", tags=["insights"])

# Mock AI insights (replace with ML logic later)
mock_overview = {
    "totalInsights": 47,
    "highRiskEmployees": 8,
    "improvementOpportunities": 23,
    "coachingRecommendations": 34,
    "predictiveAccuracy": 94.2,
    "trendsIdentified": 12,
}

mock_performance = [
    {
        "id": 1,
        "employee": "Sarah Chen",
        "avatar": "/professional-woman-diverse.png",
        "role": "Senior Software Engineer",
        "currentPerformance": 92,
        "predictedPerformance": 96,
        "confidence": 87,
        "trend": "improving",
        "riskLevel": "low",
        "keyFactors": ["Consistent goal completion", "Positive peer feedback", "Skill development progress"],
        "recommendations": ["Consider for leadership role", "Assign mentoring responsibilities"],
    },
    {
        "id": 2,
        "employee": "David Kim",
        "avatar": "/professional-analyst.png",
        "role": "Data Analyst",
        "currentPerformance": 85,
        "predictedPerformance": 78,
        "confidence": 82,
        "trend": "declining",
        "riskLevel": "medium",
        "keyFactors": ["Missed recent deadlines", "Lower engagement scores", "Skill gap in new technologies"],
        "recommendations": ["Provide additional training", "Schedule 1:1 coaching sessions", "Adjust workload"],
    },
]

mock_metrics = [
    {"month": "Jan", "actual": 85, "predicted": 87, "accuracy": 97},
    {"month": "Feb", "actual": 87, "predicted": 89, "accuracy": 95},
    {"month": "Mar", "actual": 89, "predicted": 88, "accuracy": 98},
    {"month": "Apr", "actual": 88, "predicted": 90, "accuracy": 94},
]

@router.get("/overview")
async def get_overview():
    return mock_overview

@router.get("/performance")
async def get_performance():
    return mock_performance

@router.get("/metrics")
async def get_metrics():
    return mock_metrics

@router.post("/train")
async def train_insights(current_user=Depends(get_current_active_user)):
    # admin-only
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    result = await train_model()
    return result

@router.get("/employee/{employee_id}")
async def employee_insight(employee_id: str, current_user=Depends(get_current_active_user)):
    # allow any authenticated user to view insights
    try:
        out = await predict_employee(employee_id)
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/goal/{goal_id}")
async def goal_insight(goal_id: str, current_user=Depends(get_current_active_user)):
    try:
        out = await predict_goal_probability(goal_id)
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
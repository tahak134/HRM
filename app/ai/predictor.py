# app/ai/predictor.py

import joblib
from pathlib import Path
from datetime import datetime
from app.ai._utils import days_since, safe_div

from app.models.employee import Employee
# ✅ Import directly from performance
from app.models.performance import Goal, PerformanceReview, Feedback

MODELS_DIR = Path("app/ai/models")
PERF_MODEL_PATH = MODELS_DIR / "performance_regressor.joblib"
GOAL_MODEL_PATH = MODELS_DIR / "goal_classifier.joblib"
META_PATH = MODELS_DIR / "meta.joblib"


def _load_models():
    perf = None
    goal = None
    meta = None
    if PERF_MODEL_PATH.exists():
        perf = joblib.load(PERF_MODEL_PATH)
    if GOAL_MODEL_PATH.exists():
        goal = joblib.load(GOAL_MODEL_PATH)
    if META_PATH.exists():
        meta = joblib.load(META_PATH)
    return perf, goal, meta


async def _get_employee_by_id(eid):
    """Try multiple strategies to find an employee by ID or employee_id"""
    emp = None
    try:
        emp = await Employee.get(eid)
        if emp:
            return emp
    except Exception:
        pass
    try:
        emp = await Employee.find_one({"employee_id": eid})
        if emp:
            return emp
    except Exception:
        pass
    try:
        emp = await Employee.find_one({"_id": eid})
        if emp:
            return emp
    except Exception:
        pass
    return None


async def features_for_employee(emp):
    """Build feature vector for an employee using goals, reviews, and feedback"""
    emp_id = str(emp.id)

    # Goals
    goals = await Goal.find({"owner_employee_id": emp_id}).to_list()
    num_goals = len(goals)
    completed_goals = sum(1 for g in goals if getattr(g, "status", "").lower() in ("completed", "done"))
    goal_completion_rate = safe_div(completed_goals, num_goals)

    # Performance Reviews
    reviews = await PerformanceReview.find({"employee_id": emp_id}).to_list()
    avg_review_score = None
    if reviews:
        scores = [getattr(r, "overall_rating", 0) for r in reviews]
        avg_review_score = float(sum(scores) / len(scores))

    # Feedback
    feedbacks = await Feedback.find({"receiver_id": emp_id}).to_list()
    avg_feedback_rating = None
    if feedbacks:
        ratings = [getattr(f, "rating", 0) or 0 for f in feedbacks]
        if ratings:
            avg_feedback_rating = float(sum(ratings) / len(ratings))

    last_review_date = max((getattr(r, "created_at", None) for r in reviews), default=None)
    days_since_review = days_since(last_review_date) or 9999
    engagement_score = getattr(emp, "engagement_score", 0) or 0

    return {
        "employee_id": emp_id,
        "num_goals": num_goals,
        "goal_completion_rate": goal_completion_rate,
        "avg_review_score": avg_review_score,
        "avg_feedback_rating": avg_feedback_rating,
        "days_since_review": days_since_review,
        "engagement_score": engagement_score,
    }


async def predict_employee(employee_id: str):
    """Predict employee performance using ML model or heuristic fallback"""
    perf_model, goal_model, meta = _load_models()
    emp = await _get_employee_by_id(employee_id)
    if not emp:
        raise ValueError("Employee not found")

    feats = await features_for_employee(emp)
    X = [[
        feats["num_goals"],
        feats["goal_completion_rate"],
        feats["avg_feedback_rating"] or 0,
        feats["days_since_review"],
        feats["engagement_score"],
    ]]

    predicted_perf = None
    if perf_model:
        predicted_perf = float(perf_model.predict(X)[0])
    else:
        # fallback heuristic
        feedback_score = (feats["avg_feedback_rating"] or 3)
        predicted_perf = (feedback_score * 20 * 0.5) + ((feats["goal_completion_rate"] or 0.5) * 50)

    # Rule-based recommendations
    recs = []
    if feats["goal_completion_rate"] < 0.5:
        recs.append("Focus on finishing active goals — break them into smaller milestones and clear blockers.")
    if feats["avg_feedback_rating"] and feats["avg_feedback_rating"] < 3:
        recs.append("Peer feedback suggests issues; schedule a 1:1 with the manager to identify improvements.")
    if feats["engagement_score"] and feats["engagement_score"] < 40:
        recs.append("Engagement is low — consider pairing with a mentor and setting short-term wins.")
    if not recs:
        recs.append("Solid performance. Consider stretch goals or leadership opportunities.")

    return {
        "employee_id": feats["employee_id"],
        "predicted_performance": round(predicted_perf, 2),
        "features": feats,
        "recommendations": recs,
        "meta": meta or {},
    }


async def predict_goal_probability(goal_id: str):
    """Predict probability of a goal being achieved"""
    goal = await Goal.find_one({"goal_id": goal_id})
    if not goal:
        try:
            goal = await Goal.get(goal_id)
        except Exception:
            pass
    if not goal:
        goal = await Goal.find_one({"_id": goal_id})
    if not goal:
        raise ValueError("Goal not found")

    _, goal_model, meta = _load_models()

    progress = getattr(goal, "progress_percentage", getattr(goal, "progress", 0)) or 0
    days_left = 0
    if getattr(goal, "due_date", None):
        days_left = max(0, (goal.due_date - datetime.utcnow()).days)
    num_assignees = len(getattr(goal, "assignees", []) or [])
    X = [[progress, days_left, num_assignees]]

    prob = None
    if goal_model:
        try:
            prob = float(goal_model.predict_proba(X)[0][1]) * 100
        except Exception:
            prob = float(goal_model.predict(X)[0]) * 100
    else:
        # fallback heuristic
        prob = max(0, min(100, progress * 100 * 0.6 + (100 - min(days_left, 100)) * 0.4))

    return {
        "goal_id": str(getattr(goal, "goal_id", getattr(goal, "id", goal_id))),
        "probability": round(prob, 2),
        "meta": meta or {},
    }

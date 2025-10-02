from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Dict
from app.models.performance import GoalStatus, ReviewType, FeedbackType, Feedback, PerformanceReview
from app.schemas.common import MongoModel
from pydantic import Field


class MilestoneCreate(BaseModel):
    title: str
    due_date: datetime
    notes: Optional[str] = None

class MilestoneUpdate(BaseModel):
    completed: bool
    completed_date: Optional[datetime] = None
    notes: Optional[str] = None

class MilestoneResponse(BaseModel):
    title: str
    due_date: Optional[datetime] = None
    completed: bool = False
    notes: Optional[str] = None


class GoalBase(BaseModel):
    title: str
    description: str
    category: str
    type: str
    priority: str
    start_date: datetime
    due_date: datetime
    target_value: Optional[float] = None
    unit_of_measurement: Optional[str] = None

class GoalCreate(GoalBase):
    parent_goal_id: Optional[str] = None
    aligned_with: List[str] = []
    owner_employee_id: Optional[str] = None
    team_id: Optional[str] = None

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[GoalStatus] = None
    progress_percentage: Optional[float] = None
    current_value: Optional[float] = None

class GoalResponse(MongoModel, GoalBase):
    status: GoalStatus
    goal_id: str
    progress_percentage: float
    achievement_probability: Optional[float] = None
    owner_employee_id: Optional[str] = None
    risk_factors: List[str] = []
    recommendations: List[str] = []
    department: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    milestones: List[MilestoneResponse] = []

class GoalDependencyCreate(BaseModel):
    from_goal_id: str
    to_goal_id: str
    dep_type: Optional[str] = "blocks"
    note: Optional[str] = None

class GoalAssignmentCreate(BaseModel):
    goal_id: str
    assignee_id: str
    role: Optional[str] = "contributor"
    allocation_percent: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class PerformanceReviewCreate(BaseModel):
    employee_id: str
    reviewer_id: str
    review_type: ReviewType
    review_period_start: datetime
    review_period_end: datetime
    overall_rating: float
    department: str

class PerformanceReviewUpdate(BaseModel):
    overall_rating: Optional[float] = None
    ratings: Optional[Dict[str, float]] = None
    strengths: Optional[List[str]] = None
    areas_for_improvement: Optional[List[str]] = None
    manager_comments: Optional[str] = None
    status: Optional[str] = None

class PerformanceReviewResponse(MongoModel):
    review_id: str
    employee_id: str
    reviewer_id: str
    review_type: ReviewType
    overall_rating: Optional[float] = None
    status: str
    department: str
    created_at: datetime
    performance_prediction: Optional[Dict] = None

class FeedbackCreate(BaseModel):
    employee_id: str
    giver_id: str
    feedback_type: FeedbackType
    content: str
    rating: Optional[float] = None
    categories: List[str] = []
    is_anonymous: bool = False
    related_project: Optional[str] = None
    related_goal_id: Optional[str] = None

class FeedbackResponse(MongoModel):
    feedback_id: str
    employee_id: str = Field(alias="receiver_id")
    given_by: str = Field(alias="giver_id")
    feedback_type: FeedbackType
    content: str
    sentiment: Optional[str] = None
    rating: Optional[float] = None
    created_at: datetime
    is_read: bool

class CoachingSessionCreate(BaseModel):
    employee_id: str
    coach_id: str
    session_date: datetime
    duration_minutes: int
    session_type: str
    topics_discussed: List[str] = []
    goals_set: List[str] = []
    coach_notes: Optional[str] = None

class CoachingRecommendation(BaseModel):
    employee_id: str
    recommendations: List[str]
    identified_gaps: List[str]
    suggested_resources: List[Dict]
    priority_areas: List[str]

class CoachingSessionResponse(MongoModel):
    session_id: str
    employee_id: str
    coach_id: str
    topic: str
    notes: Optional[str] = None
    created_by: str
    created_at: datetime

class AssignmentCreate(BaseModel):
    goal_id: str
    assignee_id: str
    role: str
    allocation_percent: Optional[int] = 100

class DependencyCreate(BaseModel):
    from_goal_id: str
    to_goal_id: str

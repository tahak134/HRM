from beanie import Document, Indexed, PydanticObjectId, Link
from pydantic import Field, BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List, Dict, Annotated
from enum import Enum
import uuid

def _id(prefix: str):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

class GoalStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DependencyType(str, Enum):
    BLOCKS = "blocks"
    RELATED = "related"
    SUPPORTS = "supports"

class AssignmentRole(str, Enum):
    OWNER = "owner"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"

class GoalAssignee(BaseModel):
    assignee_id: str
    role: AssignmentRole = AssignmentRole.CONTRIBUTOR
    allocation_percent: Optional[float] = None  # 0-100
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[str] = None

class ReviewType(str, Enum):
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    PROBATION = "probation"
    PROJECT = "project"

class FeedbackType(str, Enum):
    PEER = "peer"
    MANAGER = "manager"
    SUBORDINATE = "subordinate"
    SELF = "self"
    CUSTOMER = "customer"

class Goal(Document):
    goal_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("GOL"))

    owner_employee_id: Optional[str] = None
    title: str
    description: str
    
    # Goal Details
    category: str  # OKR, KPI, Personal Development
    type: str  # Individual, Team, Department, Company
    priority: str  # High, Medium, Low
    department: Optional[str] = None
    
    # Timeline
    start_date: datetime
    due_date: datetime
    completed_date: Optional[datetime] = None
    
    # Progress
    status: GoalStatus = GoalStatus.NOT_STARTED
    progress_percentage: float = 0.0
    milestones: List[Dict] = []  # {title, due_date, completed, notes}
    
    # Metrics
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit_of_measurement: Optional[str] = None
    
    # Relationships
    parent_goal_id: Optional[str] = None
    dependent_goals: List[str] = []
    aligned_with: List[str] = []  # Company/Department goals
    assignees: List[GoalAssignee] = []
    
    # AI Features
    achievement_probability: Optional[float] = None
    risk_factors: List[str] = []
    recommendations: List[str] = []
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: Optional[str] = None
    
    class Settings:
        name = "goals"
        indexes = [
            "goal_id",
            "employee_id",
            "status",
            "due_date",
            [("employee_id", 1), ("status", 1)]
        ]

class GoalDependency(Document):
    dependency_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("GDEP"))
    from_goal_id: Annotated[str, Indexed()] = Field(...)  # dependent goal
    to_goal_id: Annotated[str, Indexed()] = Field(...)    # prerequisite goal
    dep_type: DependencyType = DependencyType.BLOCKS
    note: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "goal_dependencies"
        indexes = [
            "dependency_id",
            [("from_goal_id", 1), ("to_goal_id", 1)]
        ]

class GoalAssignment(Document):
    assignment_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("GASS"))
    goal_id: Annotated[str, Indexed()] = Field(...)
    assignee_id: Annotated[str, Indexed()] = Field(...)
    role: AssignmentRole = AssignmentRole.CONTRIBUTOR
    allocation_percent: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assigned_by: Optional[str] = None
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Settings:
        name = "goal_assignments"
        indexes = [
            "assignment_id",
            [("goal_id", 1), ("assignee_id", 1)]
        ]

class PerformanceReview(Document):
    review_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("REV"))
    employee_id: Annotated[str, Indexed()] = Field(...)
    reviewer_id: str
    review_type: ReviewType
    review_period_start: datetime
    review_period_end: datetime
    
    # Review Details
    overall_rating: float  # 1-5 scale
    ratings: Dict[str, float] = {}  # {category: rating}
    department: str
       
    # Feedback
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    achievements: List[str] = []
    
    # Goals
    goals_achieved: List[str] = []  # Goal IDs
    goals_missed: List[str] = []
    
    # Comments
    self_assessment: Optional[str] = None
    manager_comments: Optional[str] = None
    employee_comments: Optional[str] = None
    
    # 360 Feedback
    feedback_collected: List[str] = []  # Feedback IDs
    
    # Status
    status: str = "draft"  # draft, submitted, reviewed, finalized
    submitted_date: Optional[datetime] = None
    finalized_date: Optional[datetime] = None
    
    # AI Insights
    performance_prediction: Optional[Dict] = None
    recommended_actions: List[str] = []
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "performance_reviews"
        indexes = [
            "review_id",
            "employee_id",
            "reviewer_id",
            "review_type",
            "status"
        ]

class Feedback(Document):
    feedback_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("FBD"))
    receiver_id: Annotated[str, Indexed()] = Field(...)
    giver_id: Annotated[str, Indexed()] = Field(...)
    feedback_type: FeedbackType
    
    # Content
    content: str
    rating: Optional[float] = None
    categories: List[str] = []  # Skills/Competencies
    
    # Anonymity
    is_anonymous: bool = False
    
    # Sentiment Analysis
    sentiment_score: Optional[float] = None  # -1 to 1
    sentiment: Optional[str] = None  # positive, neutral, negative
    
    # Context
    related_project: Optional[str] = None
    related_goal_id: Optional[str] = None
    review_id: Optional[str] = None  # If part of a review cycle
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False
    read_at: Optional[datetime] = None
    
    class Settings:
        name = "feedback"
        indexes = [
            "feedback_id",
            "employee_id",
            "given_by",
            "feedback_type",
            "created_at"
        ]

class CoachingSession(Document):
    session_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("CSES"))
    employee_id: Annotated[str, Indexed()] = Field(...)
    coach_id: Annotated[str, Indexed()] = Field(...)
    
    # Session Details
    session_date: datetime
    duration_minutes: int
    session_type: str  # one-on-one, group, workshop
    
    # Content
    topics_discussed: List[str] = []
    goals_set: List[str] = []
    action_items: List[Dict] = []  # {item, due_date, status}
    
    # Notes
    coach_notes: Optional[str] = None
    employee_notes: Optional[str] = None
    
    # Follow-up
    follow_up_required: bool = False
    next_session_date: Optional[datetime] = None
    
    # AI Recommendations
    ai_suggestions: List[str] = []
    identified_gaps: List[str] = []
    
    # System Fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "coaching_sessions"
        indexes = [
            "session_id",
            "employee_id",
            "coach_id",
            "session_date"
        ]

class DevelopmentPlan(Document):
    plan_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: _id("DPL"))
    employee_id: Annotated[str, Indexed()] = Field(...)
    title: str
    description: Optional[str] = None
    recommended_training: Optional[str] = None
    target_date: Optional[date] = None
    status: str = "planned"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None

    class Settings:
        name = "development_plans"
        indexes = [
            "plan_id",
            "employee_id",
            "status"
        ]
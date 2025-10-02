from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.schemas.performance import GoalCreate, GoalUpdate, GoalResponse
from app.models.performance import Goal
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/goals", tags=["goals"])


@router.get("/", response_model=List[GoalResponse])
async def get_goals(department: Optional[str] = Query(None)):
    """
    Get all goals. If a department is provided, filter goals
    directly by the 'department' field on the goal document.
    """
    try:
        query = {}
        if department:
            query["department"] = department

        goals = await Goal.find(query).to_list()
        return goals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=GoalResponse)
async def get_goal(id: str):
    goal = await Goal.get(id)
    if not goal:
        raise HTTPException(404, "Goal not found")
    return goal

@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal: GoalCreate,
    current_user: dict = Depends(get_current_user) # Get the logged-in user
):
    g = Goal(
        **goal.dict(), 
        created_by=current_user.get("user_id"),
        department=current_user.get("department")
    )
    await g.insert()
    return g

@router.put("/{id}", response_model=GoalResponse)
async def update_goal(id: str, goal: GoalUpdate):
    g = await Goal.get(id)
    if not g:
        raise HTTPException(404, "Goal not found")
    await g.set(goal.dict(exclude_unset=True))
    return g

@router.delete("/{id}")
async def delete_goal(id: str):
    g = await Goal.get(id)
    if not g:
        raise HTTPException(404, "Goal not found")
    await g.delete()
    return {"message": "Goal deleted"}

@router.put("/{id}/progress")
async def update_goal_progress(id: str, progress: dict):
    g = await Goal.get(id)
    if not g:
        raise HTTPException(404, "Goal not found")
    g.progress_percentage = progress.get("progress", 0)
    await g.save()
    return {"goal_id": id, "progress": g.progress_percentage}

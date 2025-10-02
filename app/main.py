# app/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.mongo_client import connect_to_mongo, close_mongo_connection
from app.config import settings
from app.models.employee import Employee, EmergencyContact, EmploymentHistory, JobDetails
from app.models.performance import Goal, GoalDependency, GoalAssignment, PerformanceReview, Feedback, DevelopmentPlan
from app.models.documents import Document, DocumentVersion
from app.models.audit import AuditLog
from app.modules.job_requisition.routes import router as job_req_router

from app.api.v1 import auth, employees, goals, performance, documents, insights
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="EPM Backend")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Later you can add your deployed frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await connect_to_mongo([
        Employee, EmergencyContact, EmploymentHistory, JobDetails,
        Goal, GoalDependency, GoalAssignment, PerformanceReview, Feedback, DevelopmentPlan,
        Document, DocumentVersion, AuditLog
    ])

app.include_router(employees.router)
app.include_router(performance.router)
app.include_router(documents.router)
app.include_router(auth.router)
app.include_router(goals.router)
app.include_router(insights.router)
app.include_router(job_req_router)

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

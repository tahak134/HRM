# core/mongo_client.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
from app.config import settings

logger = logging.getLogger(__name__)
client = None
database = None

async def connect_to_mongo(document_models: list):
    """Initialize MongoDB connection and Beanie with document models."""
    global client, database
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.database_name]
        from app.models.employee import Employee, EmergencyContact, EmploymentHistory
        from app.models.performance import Goal, PerformanceReview, Feedback, CoachingSession
        from app.models.documents import Document, DocumentVersion
        from app.models.audit import AuditLog
        # Initialize Beanie with all document models
        await init_beanie(database=database, document_models=[
            Employee, EmergencyContact, EmploymentHistory,
            Goal, PerformanceReview, Feedback, CoachingSession,
            Document, DocumentVersion, AuditLog
        ])
        logger.info("Connected to MongoDB and initialized models")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close the MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")

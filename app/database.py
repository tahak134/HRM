# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    global user_collection
    """Create database connection."""
    try:
        mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
        mongodb.database = mongodb.client[settings.database_name]

        # Import all models here (for Beanie ODM)
        from app.models.employee import Employee, EmergencyContact, EmploymentHistory
        from app.models.performance import Goal, PerformanceReview, Feedback, CoachingSession
        from app.models.documents import Document, DocumentVersion
        from app.models.audit import AuditLog

        # Initialize beanie with all document models (except users for now)
        await init_beanie(
            database=mongodb.database,
            document_models=[
                Employee, EmergencyContact, EmploymentHistory,
                Goal, PerformanceReview, Feedback, CoachingSession,
                Document, DocumentVersion,
                AuditLog
            ]
        )

        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection."""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

import asyncio
from app.database import connect_to_mongo, close_mongo_connection
from app.models.employee import Employee
from app.core.security import get_password_hash
from datetime import datetime

async def seed_admin():
    await connect_to_mongo()

    # Check if admin already exists
    existing = await Employee.find_one(Employee.email == "admin@company.com")
    if existing:
        print("Admin already exists:", existing.email)
        await close_mongo_connection()
        return

    admin = Employee(
        first_name="System",
        last_name="Admin",
        email="admin@company.com",
        phone="+123456789",
        date_of_birth=datetime(1990, 1, 1),
        department="hr",
        position="Administrator",
        job_title="HR Admin",
        hire_date=datetime.utcnow(),
        employment_type="full-time",
        address="HQ",
        city="Karachi",
        state="Sindh",
        country="Pakistan",
        postal_code="00000",
        hashed_password=get_password_hash("admin@123"),  # set secure password
        role="admin",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await admin.insert()
    print("Admin user created:", admin.email)

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_admin())

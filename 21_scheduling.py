from fastapi import FastAPI
from agno.db.sqlite import SqliteDb
from agno.scheduler import ScheduleManager


app = FastAPI(
    title="GramSwaram Scheduler",
    version="1.0.0",
)


# Database used to store schedules
db = SqliteDb(
    db_file="scheduler.db"
)

schedule_manager = ScheduleManager(db)


@app.post("/farmer-reminder")
def farmer_reminder():
    print("🌾 Farmer reminder task executed!")

    return {
        "message": "🌾 Good morning! Check your crops and irrigation today."
    }


@app.post("/create-schedule")
def create_schedule():

    schedule = schedule_manager.create(
        name="daily-farmer-reminder",
        cron="0 9 * * *",
        endpoint="http://localhost:8000/farmer-reminder",
        method="POST",
        description="Daily farmer reminder",
        timezone="Asia/Kolkata",
    )

    return {
        "message": "Schedule created successfully",
        "schedule": str(schedule),
    }
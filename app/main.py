from fastapi import FastAPI

from app.database.connection import Base, engine

# Existing routes
from app.routes.detection import router as detection_router

# New activity route
from app.routes.activity import router as activity_router

# Models
from app.models.detection_event import DetectionEvent
from app.models.activity_event import ActivityEvent


app = FastAPI(
    title="DeepStream FastAPI",
    description="Video detection and activity processing API",
    version="1.0.0"
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# ROUTES
# ============================================================

app.include_router(detection_router)

app.include_router(activity_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "DeepStream FastAPI is running"
    }
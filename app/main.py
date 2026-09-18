import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.detection import router as detection_router
from app.database.connection import Base, engine
from app.models.detection_event import DetectionEvent


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


app = FastAPI(
    title="YOLO Detection API",
    version="1.0.0"
)


# Create database tables
Base.metadata.create_all(bind=engine)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register detection routes
app.include_router(detection_router)


@app.get("/")
def root():
    return {
        "message": "YOLO Detection API is running"
    }
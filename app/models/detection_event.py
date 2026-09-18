from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from datetime import datetime

from app.database.connection import Base


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(String, unique=True, nullable=False, index=True)

    video_name = Column(String, nullable=False)
    frame_number = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)

    class_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

    bbox = Column(JSON, nullable=True)

    json_data = Column(JSON, nullable=False)

    created_on = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)

    updated_on = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String, nullable=True)

    is_creation = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
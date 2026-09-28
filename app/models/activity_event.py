from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database.connection import Base


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True, index=True)

    video_name = Column(String, nullable=False)

    total_persons = Column(Integer, nullable=False)

    person_id = Column(Integer, nullable=False)

    activity = Column(String, nullable=False)

    start_time = Column(String, nullable=False)

    end_time = Column(String, nullable=False)

    duration_seconds = Column(Float, nullable=False)

    start_frame = Column(Integer, nullable=False)

    end_frame = Column(Integer, nullable=False)

    model_name = Column(String, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
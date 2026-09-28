from pydantic import BaseModel
from typing import List


class ActivityEvent(BaseModel):
    person_id: int
    activity: str
    start_time: str
    end_time: str
    duration_seconds: float
    start_frame: int
    end_frame: int
    model_name: str
    created_at: str


class ActivityData(BaseModel):
    video_name: str
    total_persons: int
    activities: List[ActivityEvent]
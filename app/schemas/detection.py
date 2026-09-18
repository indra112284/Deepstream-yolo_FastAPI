from pydantic import BaseModel, Field
from typing import List


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox


class DetectionFrame(BaseModel):
    frame_number: int
    timestamp_seconds: float
    detections: List[Detection]


class DetectionData(BaseModel):
    video_name: str
    fps: float
    total_frames: int
    duration_seconds: float
    detections: List[DetectionFrame]
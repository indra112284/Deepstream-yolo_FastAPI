from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import hashlib
import json

from app.schemas.detection import DetectionData
from app.database.connection import get_db
from app.models.detection_event import DetectionEvent


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1/detections",
    tags=["Detections"]
)


@router.post("/")
def receive_detection(
    data: DetectionData,
    db: Session = Depends(get_db)
):
    logger.info(
        f"Detection data received: {data.video_name}"
    )

    try:
        events_created = 0
        events_skipped = 0

        for frame in data.detections:

            if frame.frame_number < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Frame number cannot be negative"
                )

            if frame.timestamp_seconds < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Timestamp cannot be negative"
                )

            for detection in frame.detections:

                if not detection.class_name.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="Class name cannot be empty"
                    )

                if not 0.0 <= detection.confidence <= 1.0:
                    raise HTTPException(
                        status_code=400,
                        detail="Confidence must be between 0 and 1"
                    )

                if detection.bbox.x1 > detection.bbox.x2:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid bounding box: x1 must be <= x2"
                    )

                if detection.bbox.y1 > detection.bbox.y2:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid bounding box: y1 must be <= y2"
                    )

                # Create a unique ID for this detection event
                event_data = {
                    "video_name": data.video_name,
                    "frame_number": frame.frame_number,
                    "class_name": detection.class_name,
                    "bbox": detection.bbox.model_dump()
                }

                event_id = hashlib.sha256(
                    json.dumps(
                        event_data,
                        sort_keys=True
                    ).encode()
                ).hexdigest()

                # Check whether this event already exists
                existing_event = (
                    db.query(DetectionEvent)
                    .filter(
                        DetectionEvent.event_id == event_id
                    )
                    .first()
                )

                if existing_event:
                    events_skipped += 1
                    continue

                event = DetectionEvent(
                    event_id=event_id,
                    video_name=data.video_name,
                    frame_number=frame.frame_number,
                    timestamp=frame.timestamp_seconds,
                    class_name=detection.class_name,
                    confidence=detection.confidence,
                    bbox=detection.bbox.model_dump(),
                    json_data=data.model_dump(),
                    created_by="yolo",
                    updated_by="yolo",
                    is_creation=True,
                    is_active=True
                )

                db.add(event)
                events_created += 1

        db.commit()

        logger.info(
            f"{events_created} detection events stored, "
            f"{events_skipped} duplicate events skipped "
            f"for {data.video_name}"
        )

        return {
            "message": "Detection processing completed",
            "video_name": data.video_name,
            "events_created": events_created,
            "events_skipped": events_skipped
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        logger.error(
            f"Failed to store detection events: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to store detection events"
        )
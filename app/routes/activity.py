from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.activity import ActivityData
from app.database.connection import get_db
from app.models.activity_event import ActivityEvent


router = APIRouter(
    prefix="/api/v1/activities",
    tags=["Activities"]
)


@router.post("/")
def receive_activity(
    data: ActivityData,
    db: Session = Depends(get_db)
):

    try:

        created_count = 0

        for activity in data.activities:

            event = ActivityEvent(
                video_name=data.video_name,
                total_persons=data.total_persons,
                person_id=activity.person_id,
                activity=activity.activity,
                start_time=activity.start_time,
                end_time=activity.end_time,
                duration_seconds=activity.duration_seconds,
                start_frame=activity.start_frame,
                end_frame=activity.end_frame,
                model_name=activity.model_name,
                created_at=activity.created_at
            )

            db.add(event)
            created_count += 1

        db.commit()

        return {
            "message": "Activity data stored successfully",
            "video_name": data.video_name,
            "total_persons": data.total_persons,
            "activities_created": created_count
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to store activity data: {str(e)}"
        )


@router.get("/")
def get_activities(
    db: Session = Depends(get_db)
):

    activities = (
        db.query(ActivityEvent)
        .order_by(ActivityEvent.id)
        .all()
    )

    return [
        {
            "id": activity.id,
            "video_name": activity.video_name,
            "total_persons": activity.total_persons,
            "person_id": activity.person_id,
            "activity": activity.activity,
            "start_time": activity.start_time,
            "end_time": activity.end_time,
            "duration_seconds": activity.duration_seconds,
            "start_frame": activity.start_frame,
            "end_frame": activity.end_frame,
            "model_name": activity.model_name,
            "created_at": activity.created_at
        }
        for activity in activities
    ]
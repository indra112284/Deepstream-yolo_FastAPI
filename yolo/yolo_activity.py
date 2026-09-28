from pathlib import Path
from datetime import datetime
import json
import cv2
import math
from ultralytics import YOLO


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

VIDEO_PATH = BASE_DIR / "videos" / "people_activity_30s.mp4.mp4"
MODEL_PATH = BASE_DIR / "yolo11n-pose.pt"

OUTPUT_DIR = BASE_DIR / "yolo" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

JSON_PATH = OUTPUT_DIR / "people_activity.json"
VIDEO_OUTPUT = OUTPUT_DIR / "people_activity_annotated.mp4"


# ============================================================
# SETTINGS
# ============================================================

CONFIDENCE = 0.15
IOU = 0.50

WALKING_THRESHOLD = 0.012
MOVEMENT_FRAMES = 8


# ============================================================
# CHECK FILES
# ============================================================

if not VIDEO_PATH.exists():
    print("ERROR: Video not found:")
    print(VIDEO_PATH)
    exit()

if not MODEL_PATH.exists():
    print("ERROR: Model not found:")
    print(MODEL_PATH)
    exit()


# ============================================================
# VIDEO INFORMATION
# ============================================================

cap = cv2.VideoCapture(str(VIDEO_PATH))

if not cap.isOpened():
    print("ERROR: Could not open video")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

duration = total_frames / fps if fps > 0 else 0

cap.release()


print()
print("======================================")
print("YOLO + BYTETRACK ACTIVITY PROCESSING")
print("======================================")
print(f"Video: {VIDEO_PATH.name}")
print(f"Model: {MODEL_PATH.name}")
print(f"Tracker: ByteTrack")
print(f"FPS: {fps:.2f}")
print(f"Total frames: {total_frames}")
print(f"Resolution: {width}x{height}")
print(f"Duration: {duration:.2f} seconds")
print()


# ============================================================
# LOAD MODEL
# ============================================================

model = YOLO(str(MODEL_PATH))

print("Model loaded successfully")
print("Starting processing...")
print()


# ============================================================
# VIDEO WRITER
# ============================================================

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(
    str(VIDEO_OUTPUT),
    fourcc,
    fps,
    (width, height)
)


# ============================================================
# PERSON DATA
# ============================================================

persons = {}

tracker_to_person = {}

next_person_id = 1

activities = []


# ============================================================
# TIME FORMAT
# ============================================================

def format_time(seconds):

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# ============================================================
# CENTER
# ============================================================

def get_center(box):

    x1, y1, x2, y2 = box

    return (
        (x1 + x2) / 2,
        (y1 + y2) / 2
    )


# ============================================================
# DISTANCE
# ============================================================

def get_distance(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


# ============================================================
# START ACTIVITY
# ============================================================

def start_activity(
    person,
    activity,
    frame_number
):

    person["current_activity"] = activity

    person["activity_start_frame"] = frame_number

    person["activity_start_time"] = (
        frame_number / fps
    )


# ============================================================
# END ACTIVITY
# ============================================================

def end_activity(
    person,
    frame_number
):

    activity = person.get("current_activity")

    if activity is None:
        return

    start_frame = person["activity_start_frame"]

    start_time = person["activity_start_time"]

    end_time = frame_number / fps

    duration_seconds = end_time - start_time

    activities.append({

        "person_id": person["person_id"],

        "activity": activity,

        "start_time": format_time(start_time),

        "end_time": format_time(end_time),

        "duration_seconds": round(
            duration_seconds,
            2
        ),

        "start_frame": start_frame,

        "end_frame": frame_number,

        "model_name": "yolo11n-pose",

        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    })

    person["current_activity"] = None


# ============================================================
# YOLO + BYTETRACK
# ============================================================

results = model.track(

    source=str(VIDEO_PATH),

    stream=True,

    tracker="bytetrack.yaml",

    classes=[0],

    conf=CONFIDENCE,

    iou=IOU,

    persist=True,

    verbose=False
)


# ============================================================
# PROCESS VIDEO
# ============================================================

for frame_number, result in enumerate(results):

    frame = result.orig_img.copy()

    detected_persons = []

    if (
        result.boxes is not None
        and result.boxes.id is not None
    ):

        boxes = result.boxes.xyxy.cpu().numpy()

        track_ids = (
            result.boxes.id
            .cpu()
            .numpy()
            .astype(int)
        )

        confidences = (
            result.boxes.conf
            .cpu()
            .numpy()
        )

        for index, tracker_id in enumerate(track_ids):

            box = boxes[index]

            confidence = float(
                confidences[index]
            )

            # =================================================
            # MAP TRACKER ID → APPLICATION PERSON ID
            # =================================================

            if tracker_id not in tracker_to_person:

                person_id = next_person_id

                next_person_id += 1

                tracker_to_person[
                    tracker_id
                ] = person_id

                persons[person_id] = {

                    "person_id": person_id,

                    "tracker_id": tracker_id,

                    "last_center": None,

                    "movement_history": [],

                    "current_activity": None,

                    "activity_start_frame": None,

                    "activity_start_time": None
                }

                print(
                    f"NEW PERSON: Person {person_id} "
                    f"(Tracker ID {tracker_id})"
                )

            person_id = tracker_to_person[
                tracker_id
            ]

            person = persons[person_id]

            # =================================================
            # CENTER
            # =================================================

            center = get_center(box)

            movement = 0.0

            if person["last_center"] is not None:

                movement = get_distance(
                    center,
                    person["last_center"]
                )

            person["last_center"] = center

            # =================================================
            # NORMALIZED MOVEMENT
            # =================================================

            diagonal = math.sqrt(
                width ** 2 +
                height ** 2
            )

            normalized_movement = (
                movement / diagonal
            )

            person["movement_history"].append(
                normalized_movement
            )

            if len(
                person["movement_history"]
            ) > MOVEMENT_FRAMES:

                person["movement_history"].pop(0)

            average_movement = (
                sum(
                    person["movement_history"]
                )
                /
                len(
                    person["movement_history"]
                )
            )

            # =================================================
            # ACTIVITY
            # =================================================

            if (
                average_movement
                >= WALKING_THRESHOLD
            ):

                activity = "walking"

            else:

                activity = "standing"

            # =================================================
            # ACTIVITY CHANGE
            # =================================================

            if person["current_activity"] is None:

                start_activity(
                    person,
                    activity,
                    frame_number
                )

            elif (
                person["current_activity"]
                != activity
            ):

                end_activity(
                    person,
                    frame_number
                )

                start_activity(
                    person,
                    activity,
                    frame_number
                )

            # =================================================
            # DRAW BOX
            # =================================================

            x1, y1, x2, y2 = map(
                int,
                box
            )

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            label = (
                f"Person {person_id} | "
                f"{activity} | "
                f"{confidence:.2f}"
            )

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            detected_persons.append(
                person_id
            )

    # =========================================================
    # FRAME INFORMATION
    # =========================================================

    cv2.putText(
        frame,
        f"Frame: {frame_number}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Persons detected: {len(detected_persons)}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    writer.write(frame)

    if frame_number % 30 == 0:

        print(
            f"Frame {frame_number}/{total_frames} "
            f"| Detected: {len(detected_persons)}"
        )


# ============================================================
# CLOSE ACTIVE ACTIVITIES
# ============================================================

for person in persons.values():

    if person["current_activity"] is not None:

        end_activity(
            person,
            total_frames - 1
        )


# ============================================================
# RELEASE
# ============================================================

writer.release()


# ============================================================
# JSON
# ============================================================

output = {

    "video_name": VIDEO_PATH.name,

    "total_persons": len(persons),

    "activities": activities

}


with open(
    JSON_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        output,
        file,
        indent=4
    )


# ============================================================
# FINAL
# ============================================================

print()
print("======================================")
print("PROCESSING COMPLETED")
print("======================================")

print(
    f"Total unique persons: {len(persons)}"
)

print(
    f"Total activity records: {len(activities)}"
)

print()
print(f"JSON: {JSON_PATH}")
print(f"Video: {VIDEO_OUTPUT}")
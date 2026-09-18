from pathlib import Path
import json
import cv2
from ultralytics import YOLO


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
VIDEOS_DIR = BASE_DIR / "videos"
OUTPUT_DIR = BASE_DIR / "yolo" / "output"

# Load YOLO model
model = YOLO("yolo11n.pt")


# Find all MP4 videos
video_files = sorted(VIDEOS_DIR.glob("*.mp4"))

if not video_files:
    print("No videos found.")
    exit()


for video_path in video_files:

    video_name = video_path.stem
    video_output_dir = OUTPUT_DIR / video_name
    json_file = video_output_dir / "detections.json"

    # Skip if JSON already exists
    if json_file.exists():
        print(f"SKIPPING: {video_name} - JSON already exists")
        continue

    print(f"\nPROCESSING: {video_name}")

    video_output_dir.mkdir(parents=True, exist_ok=True)

    # Get video information
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print(f"ERROR: Could not open {video_name}")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    cap.release()

    print(f"FPS: {fps:.2f}")
    print(f"Total frames: {total_frames}")
    print(f"Duration: {duration:.2f} seconds")

    detection_events = []

    # Run YOLO frame by frame
    results = model.predict(
        source=str(video_path),
        stream=True,
        verbose=False
    )

    for frame_number, result in enumerate(results):

        detections = []

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            detections.append({
                "class_name": model.names[class_id],
                "confidence": round(confidence, 4),
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
            })

        # Store event for this frame
        detection_events.append({
            "frame_number": frame_number,
            "timestamp_seconds": round(frame_number / fps, 3) if fps > 0 else 0,
            "detections": detections
        })

        if frame_number % 100 == 0:
            print(f"Processed frame: {frame_number}/{total_frames}")

    # Complete JSON
    output_data = {
        "video_name": video_path.name,
        "fps": round(fps, 2),
        "total_frames": total_frames,
        "duration_seconds": round(duration, 2),
        "detections": detection_events
    }

    # Save JSON
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4)

    print(f"COMPLETED: {video_name}")
    print(f"JSON saved: {json_file}")


print("\nAll videos checked.")
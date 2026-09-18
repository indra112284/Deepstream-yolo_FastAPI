# YOLO Detection with FastAPI and PostgreSQL

## Project Overview

This project processes video files using YOLO object detection, generates detection results in JSON format, sends the results to a FastAPI backend, validates the detection data, and stores the validated detection events in PostgreSQL.

## Project Flow

Videos
    ↓
YOLO Object Detection
    ↓
Detection JSON
    ↓
FastAPI
    ↓
Pydantic Validation
    ↓
Detection Event Validation
    ↓
Duplicate Event Check
    ↓
PostgreSQL
    ↓
Detection Events Table

## Technologies Used

- Python
- YOLO / Ultralytics
- OpenCV
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- psycopg2
- python-dotenv
- Postman
- pgAdmin
- Git
- GitHub

## Project Structure

deepstream_fastapi/
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
│
├── videos/
│
├── yolo/
│   ├── yolo_detection.py
│   ├── models/
│   └── output/
│
└── app/
    ├── main.py
    │
    ├── routes/
    │   └── detection.py
    │
    ├── schemas/
    │   └── detection.py
    │
    ├── models/
    │   └── detection_event.py
    │
    └── database/
        └── connection.py

## YOLO Detection

YOLO is used to process the input videos and detect objects frame by frame.

The detection results are generated in JSON format.

Each detection contains:

- Frame number
- Timestamp
- Class name
- Confidence score
- Bounding box coordinates

Example detection:

~~~json
{
    "class_name": "person",
    "confidence": 0.85,
    "bbox": {
        "x1": 100.0,
        "y1": 50.0,
        "x2": 300.0,
        "y2": 400.0
    }
}
~~~

The JSON contains:

- Video name
- FPS
- Total frames
- Duration
- Frame-wise detection results

## FastAPI

FastAPI is used as the backend API to receive YOLO detection results.

The API endpoint is:

~~~text
POST /api/v1/detections/
~~~

The API accepts the complete YOLO detection JSON as the request body.

## API Versioning

API versioning is implemented using:

~~~text
/api/v1/detections/
~~~

The `v1` represents version 1 of the API.

This allows future versions such as:

~~~text
/api/v2/detections/
~~~

to be introduced without affecting the existing API.

## Pydantic Validation

Pydantic models are used to validate incoming detection data before storing it in PostgreSQL.

The validation checks:

- Video name
- FPS
- Total frames
- Duration
- Frame number
- Timestamp
- Class name
- Confidence value
- Bounding box values

Confidence must be between:

~~~text
0.0 and 1.0
~~~

Invalid values are rejected by the API.

## Detection Event Validation

Additional validation is performed before storing detection events.

The API checks:

- Frame number cannot be negative.
- Timestamp cannot be negative.
- Class name cannot be empty.
- Confidence must be between 0 and 1.
- `x1` must be less than or equal to `x2`.
- `y1` must be less than or equal to `y2`.

Invalid detection events are rejected.

## Duplicate Event Protection

Duplicate detection events are prevented using a unique `event_id`.

The `event_id` is generated using a SHA-256 hash based on:

- Video name
- Frame number
- Class name
- Bounding box

Before inserting a detection event, the API checks whether the same `event_id` already exists.

If it already exists:

~~~text
Event is skipped
~~~

Otherwise:

~~~text
Event is inserted into PostgreSQL
~~~

## PostgreSQL

PostgreSQL is used to store validated detection events.

The main table is:

~~~text
detection_events
~~~

The table contains:

- id
- event_id
- video_name
- frame_number
- timestamp
- class_name
- confidence
- bbox
- json_data
- created_on
- created_by
- updated_on
- updated_by
- is_creation
- is_active

## JSON Data Storage

The complete YOLO detection JSON response is stored in the:

~~~text
json_data
~~~

column.

This preserves the complete detection response along with the individual detection event.

## Database Connection

SQLAlchemy is used to connect FastAPI with PostgreSQL.

The database credentials are stored in the `.env` file.

Example:

~~~text
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
~~~

The `.env` file is not committed to GitHub.

## Logging

Python logging is implemented in the FastAPI application.

Logging is used to record:

- Detection data received
- Number of events created
- Number of duplicate events skipped
- Database errors

Example log:

~~~text
Detection data received: video_name.mp4
~~~

Another example:

~~~text
77 detection events stored, 0 duplicate events skipped
~~~

## CORS

CORS (Cross-Origin Resource Sharing) is configured in FastAPI.

It allows requests from different origins to access the API.

Current configuration allows:

~~~text
allow_origins = ["*"]
~~~

CORS methods and headers are also allowed.

## API Testing

The FastAPI API was tested using:

- Swagger UI
- Postman

Swagger documentation is available at:

~~~text
http://127.0.0.1:8000/docs
~~~

Postman endpoint:

~~~text
POST http://127.0.0.1:8000/api/v1/detections/
~~~

The actual YOLO-generated JSON files were sent through the API.

## Validation Testing

The API validation was tested with invalid confidence values.

Example:

~~~text
confidence = 1.5
~~~

The API correctly rejected the invalid value because confidence must be between 0 and 1.

## Running the Project

Install the required packages:

~~~powershell
python -m pip install -r requirements.txt
~~~

Run the FastAPI application:

~~~powershell
python -m uvicorn app.main:app --reload
~~~

Open Swagger:

~~~text
http://127.0.0.1:8000/docs
~~~

## Requirements

The project uses the following Python packages:

~~~text
fastapi
uvicorn
ultralytics
opencv-python
numpy
sqlalchemy
psycopg2-binary
python-dotenv
~~~

## GitHub Security

The following files and sensitive information should not be pushed to GitHub:

- `.env`
- Database passwords
- Large video files
- Model files
- Temporary generated files

The `.gitignore` file is used to exclude these files.

Example:

~~~text
.env
__pycache__/
*.pyc
*.log
*.mp4
*.avi
*.pt
yolo/output/
~~~

## Detection Processing Results

The current implementation processed four video JSON files.

Detection events stored:

- Video 1: 77 events
- Video 2: 1,130 events
- Video 3: 1,809 events
- Video 4: 4,102 events

Total detection events:

~~~text
7,118
~~~

## Current Implementation

The current implementation completes the following workflow:

~~~text
Video
  ↓
YOLO Object Detection
  ↓
JSON Detection Results
  ↓
FastAPI API
  ↓
Pydantic Validation
  ↓
Detection Event Validation
  ↓
Duplicate Event Check
  ↓
PostgreSQL
  ↓
Detection Events Stored
~~~

## Completed Work

- YOLO object detection implemented.
- Video frames processed using YOLO.
- Detection results generated in JSON format.
- FastAPI backend implemented.
- API versioning implemented using `/api/v1/`.
- Pydantic request validation implemented.
- Detection event validation implemented.
- Duplicate detection protection implemented.
- PostgreSQL database connected using SQLAlchemy.
- Detection events stored in PostgreSQL.
- Complete JSON response stored in `json_data`.
- Logging implemented.
- CORS configured.
- Swagger API testing completed.
- Postman API testing completed.
- Four video JSON files processed.
- 7,118 detection events stored in PostgreSQL.

## DeepStream

DeepStream integration is planned as the next stage.

The intended production flow is:

~~~text
Video
  ↓
DeepStream
  ↓
YOLO / AI Model
  ↓
AI Detection Results
  ↓
FastAPI
  ↓
Validation
  ↓
PostgreSQL
~~~

DeepStream will be tested separately on an NVIDIA GPU environment.

## Project Status

Current status:

~~~text
YOLO Detection              - Completed
JSON Generation             - Completed
FastAPI                     - Completed
Pydantic Validation         - Completed
Detection Validation        - Completed
Duplicate Protection        - Completed
PostgreSQL Integration      - Completed
Detection Event Storage     - Completed
Logging                     - Completed
CORS                        - Completed
API Versioning              - Completed
Swagger Testing             - Completed
Postman Testing             - Completed
DeepStream Integration      - Next Stage
~~~
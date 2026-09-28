from pathlib import Path
import json
import requests


BASE_DIR = Path(__file__).resolve().parent.parent

JSON_FILE = BASE_DIR / "yolo" / "output" / "people_activity.json"

FASTAPI_URL = "http://127.0.0.1:8000/api/v1/activities/"


# ============================================================
# CHECK JSON
# ============================================================

if not JSON_FILE.exists():

    print("ERROR: JSON file not found:")
    print(JSON_FILE)
    exit()


# ============================================================
# READ JSON
# ============================================================

with open(
    JSON_FILE,
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


print("JSON loaded successfully")

print(
    "Video:",
    data["video_name"]
)

print(
    "Total persons:",
    data["total_persons"]
)

print(
    "Activities:",
    len(data["activities"])
)


# ============================================================
# SEND TO FASTAPI
# ============================================================

try:

    response = requests.post(
        FASTAPI_URL,
        json=data,
        timeout=60
    )

    print()
    print("Status:", response.status_code)
    print("Response:", response.text)

except requests.RequestException as e:

    print()
    print("ERROR:", e)
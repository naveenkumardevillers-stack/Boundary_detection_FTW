import math
import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="FTW Farmer GPS API")

PROJECT_DIR = Path(r"C:\Users\ABCOM\ftw-baselines")
HTML_FILE = PROJECT_DIR / "index.html"
OUTPUT_DIR = PROJECT_DIR / "gps_ftw_output"

MODEL_NAME = "FTW_PRUE_EFNET_B5_CCBY"
INFERENCE_YEAR = 2025
RADIUS_M = 2000


class LocationRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_m: float = Field(ge=0)


@app.get("/", response_class=HTMLResponse)
def home():
    if not HTML_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=f"HTML file not found: {HTML_FILE}",
        )

    return HTML_FILE.read_text(encoding="utf-8")


@app.post("/api/location")
def receive_location(data: LocationRequest):
    latitude = data.latitude
    longitude = data.longitude
    accuracy_m = data.accuracy_m

    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")
    print(f"GPS accuracy: {accuracy_m:.1f} metres")

    # Automatically create a bounding box around the GPS point.
    lat_delta = RADIUS_M / 111320

    cos_lat = math.cos(math.radians(latitude))
    if abs(cos_lat) < 1e-6:
        raise HTTPException(
            status_code=400,
            detail="This example does not support locations near the poles.",
        )

    lon_delta = RADIUS_M / (111320 * cos_lat)

    min_lon = max(-180, longitude - lon_delta)
    max_lon = min(180, longitude + lon_delta)
    min_lat = max(-90, latitude - lat_delta)
    max_lat = min(90, latitude + lat_delta)

    bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"

    # Ensure the FTW project and executable are available.
    if not (PROJECT_DIR / "pyproject.toml").exists():
        raise HTTPException(
            status_code=500,
            detail=f"FTW project not found at {PROJECT_DIR}",
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        "uv", "run", "ftw", "inference", "all",
        "--bbox", bbox,
        "--year", str(INFERENCE_YEAR),
        "--out", str(OUTPUT_DIR),
        "--model", MODEL_NAME,
        "--gpu", "-1",
        "--overwrite",
    ]

    print("Starting FTW inference...")
    print("Bounding box:", bbox)

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="FTW inference exceeded the 30-minute limit.",
        )
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not start FTW: {exc}",
        )

    if result.returncode != 0:
        error_text = (result.stderr or result.stdout)[-4000:]
        print(error_text)

        raise HTTPException(
            status_code=500,
            detail=(
                "FTW inference failed. Check Sentinel scene availability "
                "and the installed FTW CLI options. " + error_text
            ),
        )

    return {
        "status": "inference_completed",
        "latitude": latitude,
        "longitude": longitude,
        "accuracy_m": accuracy_m,
        "bounding_box": bbox,
        "output_directory": str(OUTPUT_DIR),
        "message": (
            "FTW inference completed. The generated output must still "
            "be inspected to find the field polygon containing the GPS point."
        ),
    }
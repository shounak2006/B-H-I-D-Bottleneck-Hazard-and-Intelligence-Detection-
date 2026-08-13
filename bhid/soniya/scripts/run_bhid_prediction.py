import csv
import math
from pathlib import Path
from datetime import datetime, timedelta


ROOT = Path(__file__).resolve().parent.parent

FEATURE_FILE = ROOT / "data" / "output" / "bhid_features.csv"
OUTPUT_FILE = ROOT / "data" / "output" / "bhid_final_predictions.csv"
ALERT_FILE = ROOT / "data" / "output" / "bhid_alerts.csv"


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

CONFIG = {
    "warning_threshold": 45.0,
    "critical_threshold": 70.0,

    # Number of consecutive frames required
    # before an alert is generated.
    "alert_persistence": 5,

    # Video FPS
    "fps": 30.0,

    # Approximate frame-space zone.
    # Can be replaced later by calibrated coordinates.
    "location": "CAM_01 / FULL_FRAME",
}


# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------

def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def calculate_risk(row):
    """
    Calculates a congestion/bottleneck risk score
    from the extracted spatiotemporal features.

    This is a deployable rule-based prediction layer.
    It is NOT claimed as a trained neural network.
    """

    count = float(row.get("pedestrian_count", 0))
    occupancy = float(row.get("occupancy_ratio", 0))
    speed = float(row.get("mean_speed_m_s", 0))
    velocity_variance = float(
        row.get("velocity_variance", 0)
    )
    entropy = float(
        row.get("directional_entropy", 0)
    )
    convergence = float(
        row.get("trajectory_convergence", 0)
    )

    # -----------------------------------------------------
    # Crowd level
    # -----------------------------------------------------

    crowd_score = clamp(count / 15.0)

    # Occupancy is already approximately 0-1
    occupancy_score = clamp(occupancy)

    # Current velocity values are pixel/sec.
    # Lower movement = higher risk.
    speed_score = 1.0 - clamp(speed / 40.0)

    # High velocity variance indicates unstable movement.
    variance_score = clamp(
        velocity_variance / 1000.0
    )

    # Directional disorder.
    entropy_score = clamp(
        entropy / 3.0
    )

    # High convergence means movement becomes aligned.
    convergence_score = clamp(convergence)

    # -----------------------------------------------------
    # Weighted risk
    # -----------------------------------------------------

    risk = (
        0.30 * crowd_score +
        0.25 * occupancy_score +
        0.20 * speed_score +
        0.10 * variance_score +
        0.10 * entropy_score +
        0.05 * convergence_score
    )

    return round(risk * 100, 2)


def classify(risk):
    if risk >= CONFIG["critical_threshold"]:
        return "BOTTLENECK_CRITICAL"

    if risk >= CONFIG["warning_threshold"]:
        return "CONGESTION_WARNING"

    return "NORMAL"


# ---------------------------------------------------------
# LOAD FEATURES
# ---------------------------------------------------------

if not FEATURE_FILE.exists():
    raise FileNotFoundError(
        f"Feature file not found:\n{FEATURE_FILE}"
    )


features = []

with open(FEATURE_FILE, newline="") as f:

    reader = csv.DictReader(f)

    for row in reader:
        features.append(row)


print("=" * 65)
print("BHID CROWD BOTTLENECK PREDICTION")
print("=" * 65)

print(f"Frames loaded: {len(features)}")


# ---------------------------------------------------------
# PREDICTION
# ---------------------------------------------------------

predictions = []

consecutive_risk_frames = 0
alerts = []

start_time = datetime.now()

for row in features:

    frame_index = int(row["frame_index"])

    timestamp_seconds = (
        frame_index / CONFIG["fps"]
    )

    risk = calculate_risk(row)

    condition = classify(risk)

    if condition != "NORMAL":
        consecutive_risk_frames += 1
    else:
        consecutive_risk_frames = 0

    alert = "NO"

    if (
        consecutive_risk_frames
        >= CONFIG["alert_persistence"]
    ):
        alert = "YES"

    timestamp = (
        start_time +
        timedelta(seconds=timestamp_seconds)
    ).isoformat(timespec="seconds")

    predictions.append({
        "timestamp": timestamp,
        "frame_index": frame_index,
        "location": CONFIG["location"],
        "pedestrian_count": row["pedestrian_count"],
        "occupancy_ratio": row["occupancy_ratio"],
        "mean_speed": row["mean_speed_m_s"],
        "risk_score": risk,
        "condition": condition,
        "alert": alert,
    })


# ---------------------------------------------------------
# SAVE FINAL CSV
# ---------------------------------------------------------

fieldnames = [
    "timestamp",
    "frame_index",
    "location",
    "pedestrian_count",
    "occupancy_ratio",
    "mean_speed",
    "risk_score",
    "condition",
    "alert",
]


OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


with open(
    OUTPUT_FILE,
    "w",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(predictions)


# ---------------------------------------------------------
# ALERT CSV
# ---------------------------------------------------------

alert_rows = [
    p for p in predictions
    if p["alert"] == "YES"
]


with open(
    ALERT_FILE,
    "w",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(alert_rows)


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

max_prediction = max(
    predictions,
    key=lambda x: x["risk_score"]
)

warning_count = sum(
    1
    for p in predictions
    if p["condition"] == "CONGESTION_WARNING"
)

critical_count = sum(
    1
    for p in predictions
    if p["condition"] == "BOTTLENECK_CRITICAL"
)


print()
print("========== FINAL RESULT ==========")

print(
    f"Maximum risk score: "
    f"{max_prediction['risk_score']}"
)

print(
    f"Peak frame: "
    f"{max_prediction['frame_index']}"
)

print(
    f"Peak condition: "
    f"{max_prediction['condition']}"
)

print(
    f"Warning frames: "
    f"{warning_count}"
)

print(
    f"Critical frames: "
    f"{critical_count}"
)

print(
    f"Alerts generated: "
    f"{len(alert_rows)}"
)

print()
print("Final prediction report:")
print(OUTPUT_FILE)

print()
print("Alert report:")
print(ALERT_FILE)

print("=" * 65)
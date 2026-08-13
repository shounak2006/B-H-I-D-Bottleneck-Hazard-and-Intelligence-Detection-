import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "output" / "tracks.csv"
OUTPUT = ROOT / "data" / "output" / "congestion_report.csv"

frames = defaultdict(list)

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        frames[int(row["frame_index"])].append(row)

results = []

for frame, people in frames.items():

    count = len(people)

    total_area = 0

    for p in people:
        total_area += (
            float(p["width"]) *
            float(p["height"])
        )

    # Pixel-space occupancy
    frame_area = 484 * 774
    occupancy = min(total_area / frame_area, 1.0)

    # More people + larger occupancy = higher congestion
    congestion_score = (
        0.6 * min(count / 20, 1.0)
        +
        0.4 * occupancy
    )

    results.append({
        "frame_index": frame,
        "pedestrian_count": count,
        "occupancy_ratio": round(occupancy, 4),
        "congestion_score": round(congestion_score, 4)
    })

results.sort(
    key=lambda x: x["congestion_score"],
    reverse=True
)

with open(OUTPUT, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "frame_index",
            "pedestrian_count",
            "occupancy_ratio",
            "congestion_score"
        ]
    )

    writer.writeheader()
    writer.writerows(results)

print("=" * 55)
print("BHID CONGESTION ANALYSIS")
print("=" * 55)

print(f"Frames analysed: {len(results)}")

print("\nTOP 10 CONGESTED FRAMES:")

for r in results[:10]:
    print(
        f"Frame {r['frame_index']:>4} | "
        f"People: {r['pedestrian_count']:>2} | "
        f"Occupancy: {r['occupancy_ratio']:.3f} | "
        f"Score: {r['congestion_score']:.3f}"
    )

print("\nReport saved:")
print(OUTPUT)
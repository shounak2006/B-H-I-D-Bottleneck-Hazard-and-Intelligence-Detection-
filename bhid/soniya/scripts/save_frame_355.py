import cv2
from pathlib import Path

video = Path("runs/detect/track/crowd.avi")

# Agar filename alag hai to yahan apne output video ka naam likhna
if not video.exists():
    videos = list(Path("runs/detect/track").glob("*"))
    video_files = [x for x in videos if x.suffix.lower() in [".avi", ".mp4", ".mov"]]

    if not video_files:
        raise FileNotFoundError("Annotated video nahi mila.")

    video = video_files[0]

cap = cv2.VideoCapture(str(video))

if not cap.isOpened():
    raise RuntimeError(f"Video open nahi hua: {video}")

cap.set(cv2.CAP_PROP_POS_FRAMES, 355)

ok, frame = cap.read()

if not ok:
    raise RuntimeError("Frame 355 read nahi hua.")

output = Path("data/output/frame_355_congestion.jpg")
output.parent.mkdir(parents=True, exist_ok=True)

cv2.imwrite(str(output), frame)

cap.release()

print("Frame saved:")
print(output.resolve())
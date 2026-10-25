from collections import defaultdict, deque, Counter
import sys
import textwrap
import tkinter as tk

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import cv2
from modules.detector import Detector
from modules.malayalam import (
    describe_scene_in_malayalam,
    format_threat_warning_in_malayalam,
)
from modules.speaker import Speaker
from modules.threat_analyzer import ThreatAnalyzer
from bytetrack_wrapper import MultiClassByteTracker


# ============================================================
# CONFIGURATION
# ============================================================

print("===================================")
print("       BlindAssist AI Vision")
print("===================================")

VIDEO_PATH = r"C:\Users\Aleena Johnson\Downloads\Person_walking_along_roadside_20261009111619.mp4"
HISTORY_LENGTH = 20
MOTION_MIN_PIXELS = 12
speaker = Speaker()
threat_analyzer = ThreatAnalyzer()
malayalam_voice_available = speaker.has_malayalam_voice()
if malayalam_voice_available:
    print("Malayalam speech voice found.")
else:
    print(
        "[WARNING] No Malayalam Windows speech voice is installed. "
        "Malayalam captions will be shown, but not spoken."
    )


class MalayalamCaptionWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BlindAssist - Malayalam Captions")
        self.root.geometry("800x160")
        self.closed = False
        self.caption = tk.StringVar(value="ക്യാപ്ഷൻ ഇവിടെ കാണിക്കും.")
        self.label = tk.Label(
            self.root,
            textvariable=self.caption,
            font=("Nirmala UI", 20),
            wraplength=760,
            justify=tk.LEFT,
            padx=20,
            pady=20,
        )
        self.label.pack(fill=tk.BOTH, expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def update(self, caption):
        if self.closed:
            return False
        self.caption.set(caption)
        self.root.update_idletasks()
        self.root.update()
        return not self.closed

    def close(self):
        if not self.closed:
            self.closed = True
            self.root.destroy()

print(f"Opening video: {VIDEO_PATH}")
video = cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    raise FileNotFoundError(
        f"Could not open video:\n{VIDEO_PATH}\n"
        "Check that the file exists and that VIDEO_PATH is correct."
    )


# ============================================================
# YOLO26s
# ============================================================

print("Starting YOLO26s...")
detector = Detector()
print("YOLO26s ready.")


# ============================================================
# BYTETrack
# ============================================================

print("Starting ByteTrack...")
class_names = detector.model.names
if isinstance(class_names, dict):
    class_names = list(class_names.values())

tracker = MultiClassByteTracker(
    class_names=class_names,
    track_thresh=0.5,
    track_buffer=30,
    match_thresh=0.8,
    low_thresh=0.1,
)
print("ByteTrack ready.")
caption_window = MalayalamCaptionWindow()


# ============================================================
# TRACKING HISTORY
# ============================================================

track_history = defaultdict(lambda: deque(maxlen=HISTORY_LENGTH))
previous_track_ids = set()
frame_number = 0
last_printed_caption = None
last_spoken_warning = None


# ============================================================
# YOLO -> BYTETrack CONVERSION
# ============================================================

def yolo_to_tracker_detections(results, detector_instance):
    """Convert the first Ultralytics result into the tracker's expected format."""
    detections = []
    if results is None or len(results) == 0:
        return detections

    result = results[0]
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return detections

    names = detector_instance.model.names
    for i in range(len(boxes)):
        try:
            x1, y1, x2, y2 = boxes.xyxy[i].tolist()
            confidence = float(boxes.conf[i].item())
            class_id = int(boxes.cls[i].item())
            if isinstance(names, dict):
                class_name = names.get(class_id, str(class_id))
            else:
                class_name = names[class_id]

            detections.append({
                "class_name": str(class_name),
                "class_id": class_id,
                "confidence": confidence,
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
            })
        except (IndexError, TypeError, ValueError, AttributeError) as exc:
            print(f"[WARNING] Skipping malformed detection {i}: {exc}")
    return detections


# ============================================================
# CONTEXTUAL, RULE-BASED SCENE DESCRIPTION (NO QWEN)
# ============================================================

def pluralize_object(name, count):
    """Simple pluralization for common object labels."""
    if count == 1:
        return name
    irregular = {"person": "people", "mouse": "mice"}
    if name in irregular:
        return irregular[name]
    if name.endswith(("bus", "class")):
        return name + "es"
    if name.endswith("y") and len(name) > 1 and name[-2].lower() not in "aeiou":
        return name[:-1] + "ies"
    if name.endswith("s"):
        return name
    return name + "s"


def get_position(center_x, frame_width):
    ratio = center_x / max(float(frame_width), 1.0)
    if ratio < 0.34:
        return "left"
    if ratio > 0.66:
        return "right"
    return "center"


def collect_scene_details(tracks, track_history, frame_width, new_track_ids=None):
    unique_tracks = {}
    for track in tracks:
        if not isinstance(track, dict) or "bbox" not in track or "class_name" not in track:
            continue
        track_id = track.get("track_id")
        unique_tracks[track_id if track_id is not None else id(track)] = track

    if not unique_tracks:
        return None

    counts = Counter(str(t.get("class_name", "object")) for t in unique_tracks.values())
    positions = []
    motions = []
    for track_id, track in unique_tracks.items():
        try:
            x1, _, x2, _ = map(float, track["bbox"])
        except (TypeError, ValueError):
            continue

        class_name = str(track.get("class_name", "object"))
        location = get_position((x1 + x2) / 2, frame_width)
        position = (class_name, location)
        if position not in positions:
            positions.append(position)

        real_track_id = track.get("track_id")
        if real_track_id is not None and real_track_id in track_history:
            points = track_history[real_track_id]
            if len(points) >= 5:
                dx = points[-1][0] - points[-5][0]
                if abs(dx) >= max(MOTION_MIN_PIXELS, frame_width * 0.015):
                    direction = "right" if dx > 0 else "left"
                    motion = (class_name, direction)
                    if motion not in motions:
                        motions.append(motion)

        if len(positions) >= 3:
            break

    newly_tracked = []
    if new_track_ids:
        for track in unique_tracks.values():
            if track.get("track_id") in new_track_ids:
                name = str(track.get("class_name", "object"))
                if name not in newly_tracked:
                    newly_tracked.append(name)

    return counts, positions, motions, newly_tracked


def describe_scene_with_context(tracks, track_history, frame_width, new_track_ids=None):
    """Describe tracked object counts, approximate image positions, and horizontal motion."""
    if not tracks:
        return "No objects are currently detected in the frame."

    details = collect_scene_details(
        tracks, track_history, frame_width, new_track_ids
    )
    if details is None:
        return "No tracked objects are currently available."

    counts, positions, motions, newly_tracked = details
    object_summary = [
        f"{count} {pluralize_object(name, count)}"
        for name, count in counts.most_common()
    ]
    object_sentence = (
        f"{object_summary[0]} is visible" if len(object_summary) == 1
        else ", ".join(object_summary[:-1]) + " and " + object_summary[-1] + " are visible"
    )

    caption = f"The scene contains {object_sentence}."
    if positions:
        position_phrases = [
            f"{name} on the {position}" for name, position in positions
        ]
        caption += " Positions: " + "; ".join(position_phrases) + "."
    if motions:
        motion_phrases = [
            f"{name} is moving across the image toward the {direction}"
            for name, direction in motions[:2]
        ]
        caption += " Movement: " + "; ".join(motion_phrases) + "."
    if newly_tracked:
        caption += " Newly tracked: " + ", ".join(newly_tracked) + "."
    return caption


def describe_scene_in_malayalam_with_context(
    tracks, track_history, frame_width, new_track_ids=None
):
    """Build an offline Malayalam caption from the tracked scene details."""
    if not tracks:
        return describe_scene_in_malayalam([], [], [], [])

    details = collect_scene_details(
        tracks, track_history, frame_width, new_track_ids
    )
    if details is None:
        return "ട്രാക്ക് ചെയ്ത വസ്തുക്കൾ ലഭ്യമല്ല."

    counts, positions, motions, newly_tracked = details
    return describe_scene_in_malayalam(
        counts.most_common(), positions, motions[:2], newly_tracked
    )


def draw_caption(frame, caption):
    """Draw a readable multi-line caption at the bottom of the video frame."""
    lines = textwrap.wrap(caption, width=72) or [caption]
    line_height = 25
    panel_height = 18 + line_height * len(lines)
    y_top = max(0, frame.shape[0] - panel_height)

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, y_top), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.68, frame, 0.32, 0, frame)

    for index, line in enumerate(lines):
        y = min(frame.shape[0] - 5, y_top + 28 + index * line_height)
        cv2.putText(frame, line, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58,
                    (255, 255, 255), 1, cv2.LINE_AA)
    return frame


# ============================================================
# MAIN LOOP
# ============================================================

try:
    while True:
        success, frame = video.read()
        if not success or frame is None:
            print("Video finished or frame could not be read.")
            break

        frame_number += 1
        results = detector.detect(frame)

        if results is None or len(results) == 0:
            detections = []
            display_frame = frame.copy()
        else:
            detections = yolo_to_tracker_detections(results, detector)
            try:
                display_frame = results[0].plot()
            except (AttributeError, IndexError, TypeError):
                display_frame = frame.copy()

        tracks = tracker.update(detections)
        if tracks is None:
            tracks = []

        current_track_ids = set()
        for track in tracks:
            if not isinstance(track, dict) or "bbox" not in track:
                continue
            try:
                x1, y1, x2, y2 = map(int, track["bbox"])
            except (TypeError, ValueError):
                continue

            class_name = str(track.get("class_name", "object"))
            track_id = track.get("track_id")
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            if track_id is not None:
                current_track_ids.add(track_id)
                track_history[track_id].append((center_x, center_y))

            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            label = f"{class_name} ID:{track_id}" if track_id is not None else class_name
            cv2.putText(display_frame, label, (x1, max(20, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.circle(display_frame, (center_x, center_y), 5, (0, 0, 255), -1)

            if track_id is not None:
                points = track_history[track_id]
                for i in range(1, len(points)):
                    cv2.line(display_frame, points[i - 1], points[i], (255, 0, 0), 2)

        new_track_ids = current_track_ids - previous_track_ids
        previous_track_ids = current_track_ids

        scene_caption = describe_scene_with_context(
            tracks, track_history, frame.shape[1], new_track_ids=new_track_ids
        )
        malayalam_caption = describe_scene_in_malayalam_with_context(
            tracks, track_history, frame.shape[1], new_track_ids=new_track_ids
        )
        threat_warnings = threat_analyzer.analyze(
            tracks, frame.shape[1], frame.shape[0], frame=frame
        )
        threat_messages = [
            format_threat_warning_in_malayalam(
                warning.class_name, warning.zone, warning.approaching
            )
            for warning in threat_warnings
        ]
        if threat_messages:
            malayalam_caption += " " + " ".join(threat_messages)

        # Draw road hazard highlights (potholes, puddles, ditches)
        for warning in threat_warnings:
            if getattr(warning, "bbox", None) is not None:
                bx1, by1, bx2, by2 = map(int, warning.bbox)
                hazard_color = (0, 0, 255) if warning.class_name in ("ditch", "gutter", "canal") else (0, 140, 255)
                cv2.rectangle(display_frame, (bx1, by1), (bx2, by2), hazard_color, 2)
                cv2.putText(
                    display_frame,
                    f"HAZARD: {warning.class_name.upper()}",
                    (bx1, max(25, by1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    hazard_color,
                    2,
                )

        cv2.putText(display_frame, f"Objects Detected: {len(detections)}", (20, 135),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Active Tracks: {len(tracks)}", (20, 165),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(display_frame, "BlindAssist AI Vision", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(display_frame, "YOLO26s: Active", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(display_frame, "Video Input: Active", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(display_frame, "ByteTrack: Active", (20, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Print only when the caption changes so the terminal is not flooded.
        caption_signature = (scene_caption, malayalam_caption)
        if caption_signature != last_printed_caption:
            print(
                f"[Frame {frame_number}] English: {scene_caption} "
                f"| Malayalam: {malayalam_caption}"
            )
            last_printed_caption = caption_signature

        if threat_messages:
            highest_priority_warning = threat_messages[0]
            if (
                malayalam_voice_available
                and highest_priority_warning != last_spoken_warning
            ):
                speaker.speak_malayalam(highest_priority_warning)
            last_spoken_warning = highest_priority_warning
        else:
            last_spoken_warning = None

        draw_caption(display_frame, scene_caption)
        if not caption_window.update(malayalam_caption):
            break
        cv2.imshow("BlindAssist AI Vision", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    print("\nStopping BlindAssist...")
    caption_window.close()
    video.release()
    cv2.destroyAllWindows()
    print("BlindAssist stopped.")

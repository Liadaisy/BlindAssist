"""Prioritize nearby or rapidly approaching navigational obstacles and road hazards."""

from dataclasses import dataclass
import math
import time
import cv2
import numpy as np


OBSTACLE_PRIORITIES = {
    # Roadside falling hazards (critical injury risk for visually impaired)
    "ditch": 115,
    "gutter": 115,
    "canal": 115,
    "stairs": 100,
    # Surface hazards (tripping/ankle injury)
    "pothole": 98,
    "car": 95,
    "bus": 95,
    "truck": 95,
    "motorcycle": 90,
    "bicycle": 85,
    "person": 75,
    # Slipping/wet hazards
    "puddle": 70,
    "door": 70,
    "bench": 65,
    "chair": 65,
}

GROUND_HAZARDS = {"ditch", "gutter", "canal", "pothole", "puddle"}
ZONE_NAMES = ("left", "center", "right")
APPROACH_RATE_THRESHOLD = 0.45
MIN_APPROACH_INTERVAL = 0.25
MAX_APPROACH_INTERVAL = 1.5
MIN_APPROACH_HEIGHT = 0.12
NEAR_HEIGHT = 0.22
NEAR_AREA = 0.10
APPROACHING_SIDE_HEIGHT = 0.20
MAX_WARNINGS = 3


@dataclass(frozen=True)
class ThreatWarning:
    class_name: str
    zone: str
    priority: int
    approaching: bool
    bbox: tuple = None


class ThreatAnalyzer:
    """Analyze tracked obstacle position, apparent approach speed, and road surface hazards."""

    def __init__(self):
        self._previous_sizes = {}

    @staticmethod
    def _get_zone(center_x, frame_width):
        relative_x = center_x / frame_width
        if relative_x < 1 / 3:
            return "left"
        if relative_x > 2 / 3:
            return "right"
        return "center"

    @staticmethod
    def _get_approach_rate(previous, current, elapsed):
        if not MIN_APPROACH_INTERVAL <= elapsed <= MAX_APPROACH_INTERVAL:
            return 0.0
        previous_height, previous_area = previous
        current_height, current_area = current
        if previous_height <= 0 or previous_area <= 0:
            return 0.0

        height_rate = (current_height / previous_height - 1) / elapsed
        area_rate = (math.sqrt(current_area / previous_area) - 1) / elapsed
        return max(height_rate, area_rate)

    def detect_road_hazards(self, frame):
        """Detect ground-level potholes, water puddles, and roadside ditch/canal edges."""
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return []

        h, w = frame.shape[:2]
        if h <= 0 or w <= 0:
            return []

        hazards = []
        y_start = int(h * 0.5)
        roi = frame[y_start:h, :]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # ----------------------------------------------------
        # 1. Pothole Detection (Dark depressions in walking path)
        # ----------------------------------------------------
        try:
            kw = max(15, int(w * 0.025) | 1)
            kh = max(11, int(h * 0.02) | 1)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kw, kh))
            blackhat = cv2.morphologyEx(gray_roi, cv2.MORPH_BLACKHAT, kernel)
            _, thresh = cv2.threshold(blackhat, 32, 255, cv2.THRESH_BINARY)
            closed = cv2.morphologyEx(
                thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            )
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            min_pothole_area = int(0.003 * w * h)
            max_pothole_area = int(0.12 * w * h)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if min_pothole_area <= area <= max_pothole_area:
                    bx, by, bw, bh = cv2.boundingRect(cnt)
                    aspect = bw / float(max(bh, 1))
                    if 0.35 <= aspect <= 2.8:
                        cx = bx + bw / 2
                        cy = by + y_start + bh / 2
                        zone = self._get_zone(cx, w)
                        priority = 98 + (10 if zone == "center" else 0) + min(int((cy / h) * 10), 10)
                        hazards.append({
                            "class_name": "pothole",
                            "zone": zone,
                            "priority": priority,
                            "bbox": (float(bx), float(by + y_start), float(bx + bw), float(by + y_start + bh)),
                        })
        except Exception as exc:
            print(f"[THREAT ANALYZER] Pothole detection error: {exc}")

        # ----------------------------------------------------
        # 2. Puddle Detection (Specular reflections / water sheen)
        # ----------------------------------------------------
        try:
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            _, s_ch, v_ch = cv2.split(hsv_roi)
            puddle_mask = ((s_ch < 45) & (v_ch > 210)).astype(np.uint8) * 255
            closed_puddle = cv2.morphologyEx(
                puddle_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            )
            p_cnts, _ = cv2.findContours(closed_puddle, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            min_puddle_area = int(0.005 * w * h)
            for cnt in p_cnts:
                area = cv2.contourArea(cnt)
                if area >= min_puddle_area:
                    bx, by, bw, bh = cv2.boundingRect(cnt)
                    cx = bx + bw / 2
                    zone = self._get_zone(cx, w)
                    hazards.append({
                        "class_name": "puddle",
                        "zone": zone,
                        "priority": 70 + (10 if zone == "center" else 0),
                        "bbox": (float(bx), float(by + y_start), float(bx + bw), float(by + y_start + bh)),
                    })
        except Exception as exc:
            print(f"[THREAT ANALYZER] Puddle detection error: {exc}")

        # ----------------------------------------------------
        # 3. Roadside Ditch / Gutter / Canal Edge Detection
        # ----------------------------------------------------
        try:
            # Check left shoulder (0 to 35% width)
            left_w = int(w * 0.35)
            left_gray = gray_roi[:, :left_w]
            edges_left = cv2.Canny(left_gray, 50, 150)
            lines_l = cv2.HoughLinesP(
                edges_left, 1, np.pi / 180, threshold=40,
                minLineLength=int(h * 0.18), maxLineGap=25
            )
            if lines_l is not None:
                steep_lines = [
                    line[0] for line in lines_l
                    if abs(line[0][3] - line[0][1]) >= abs(line[0][2] - line[0][0]) * 0.85
                ]
                if len(steep_lines) >= 2:
                    hazards.append({
                        "class_name": "ditch",
                        "zone": "left",
                        "priority": 105,
                        "bbox": (0.0, float(y_start), float(left_w), float(h)),
                    })

            # Check right shoulder (65% to 100% width)
            right_x = int(w * 0.65)
            right_gray = gray_roi[:, right_x:]
            edges_right = cv2.Canny(right_gray, 50, 150)
            lines_r = cv2.HoughLinesP(
                edges_right, 1, np.pi / 180, threshold=40,
                minLineLength=int(h * 0.18), maxLineGap=25
            )
            if lines_r is not None:
                steep_lines = [
                    line[0] for line in lines_r
                    if abs(line[0][3] - line[0][1]) >= abs(line[0][2] - line[0][0]) * 0.85
                ]
                if len(steep_lines) >= 2:
                    hazards.append({
                        "class_name": "ditch",
                        "zone": "right",
                        "priority": 105,
                        "bbox": (float(right_x), float(y_start), float(w), float(h)),
                    })
        except Exception as exc:
            print(f"[THREAT ANALYZER] Ditch edge detection error: {exc}")

        return hazards

    def analyze(self, tracks, frame_width, frame_height, timestamp=None, frame=None):
        """Return high-urgency warnings sorted by risk priority, incorporating road hazards."""
        if frame_width <= 0 or frame_height <= 0:
            raise ValueError("Frame width and height must be positive.")

        current_time = time.monotonic() if timestamp is None else float(timestamp)
        if not math.isfinite(current_time):
            raise ValueError("Timestamp must be a finite number.")

        observations = {}
        warnings = []
        for track in tracks or []:
            if not isinstance(track, dict):
                continue

            class_name = str(track.get("class_name", "")).strip().lower()
            base_priority = OBSTACLE_PRIORITIES.get(class_name)
            if base_priority is None:
                continue

            track_id = track.get("track_id")
            if track_id is None:
                continue

            try:
                x1, y1, x2, y2 = map(float, track["bbox"])
            except (KeyError, TypeError, ValueError):
                continue
            if not all(math.isfinite(value) for value in (x1, y1, x2, y2)):
                continue

            x1 = min(max(x1, 0.0), frame_width)
            x2 = min(max(x2, 0.0), frame_width)
            y1 = min(max(y1, 0.0), frame_height)
            y2 = min(max(y2, 0.0), frame_height)
            width = x2 - x1
            height = y2 - y1
            if width <= 0 or height <= 0:
                continue

            area_ratio = (width * height) / (frame_width * frame_height)
            height_ratio = height / frame_height
            zone = self._get_zone((x1 + x2) / 2, frame_width)
            key = (class_name, track_id)
            current_size = (height_ratio, area_ratio)
            previous = self._previous_sizes.get(key)
            approach_rate = 0.0
            if previous is not None:
                previous_time, previous_size = previous
                elapsed = current_time - previous_time
                if elapsed >= MIN_APPROACH_INTERVAL:
                    approach_rate = self._get_approach_rate(
                        previous_size, current_size, elapsed
                    )
                    observations[key] = (current_time, current_size)
                elif elapsed >= 0:
                    observations[key] = previous
                else:
                    observations[key] = (current_time, current_size)
            else:
                observations[key] = (current_time, current_size)

            approaching = (
                approach_rate >= APPROACH_RATE_THRESHOLD
                and height_ratio >= MIN_APPROACH_HEIGHT
            )

            near_in_center = zone == "center" and (
                height_ratio >= NEAR_HEIGHT or area_ratio >= NEAR_AREA
            )
            rapid_approach_risk = approaching and (
                zone == "center" or height_ratio >= APPROACHING_SIDE_HEIGHT
            )

            # Ground hazards evaluation
            is_ground_hazard = class_name in GROUND_HAZARDS
            ground_hazard_risk = False
            if is_ground_hazard:
                bottom_ratio = y2 / frame_height
                if class_name in ("ditch", "gutter", "canal"):
                    ground_hazard_risk = bottom_ratio >= 0.45 or area_ratio >= 0.03
                elif class_name == "pothole":
                    ground_hazard_risk = (bottom_ratio >= 0.50 or area_ratio >= 0.02) and (
                        zone == "center" or area_ratio >= 0.04
                    )
                elif class_name == "puddle":
                    ground_hazard_risk = bottom_ratio >= 0.55 or area_ratio >= 0.03

            if not near_in_center and not rapid_approach_risk and not ground_hazard_risk:
                continue

            closeness = max(
                height_ratio / NEAR_HEIGHT,
                area_ratio / NEAR_AREA,
            )
            if is_ground_hazard:
                edge_hazard_bonus = 20 if (zone == "center" or class_name in ("ditch", "gutter", "canal")) else 10
                priority = (
                    base_priority
                    + edge_hazard_bonus
                    + min(int(closeness * 10), 20)
                )
            else:
                priority = (
                    base_priority
                    + (40 if approaching else 0)
                    + (20 if zone == "center" else 0)
                    + min(int(closeness * 10), 20)
                )

            warnings.append(
                ThreatWarning(
                    class_name=class_name,
                    zone=zone,
                    priority=priority,
                    approaching=approaching,
                    bbox=(x1, y1, x2, y2),
                )
            )

        self._previous_sizes = observations

        # Incorporate computer vision road hazards from frame if provided
        if frame is not None:
            road_hazards = self.detect_road_hazards(frame)
            for hazard in road_hazards:
                warnings.append(
                    ThreatWarning(
                        class_name=hazard["class_name"],
                        zone=hazard["zone"],
                        priority=hazard["priority"],
                        approaching=False,
                        bbox=hazard.get("bbox"),
                    )
                )

        # De-duplicate by (class_name, zone), keeping the highest priority instance
        best_warnings = {}
        for warning in warnings:
            key = (warning.class_name, warning.zone)
            if key not in best_warnings or warning.priority > best_warnings[key].priority:
                best_warnings[key] = warning

        unique_warnings = list(best_warnings.values())
        unique_warnings.sort(key=lambda warning: warning.priority, reverse=True)
        return unique_warnings[:MAX_WARNINGS]


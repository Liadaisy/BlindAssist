import unittest

from modules.threat_analyzer import ThreatAnalyzer
from modules.malayalam import format_threat_warning_in_malayalam


def track(class_name, track_id, box):
    return {"class_name": class_name, "track_id": track_id, "bbox": box}


class ThreatAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = ThreatAnalyzer()

    def test_finds_close_center_obstacle_and_ignores_background_objects(self):
        warnings = self.analyzer.analyze(
            [
                track("chair", 1, [400, 250, 600, 490]),
                track("book", 2, [10, 10, 50, 50]),
            ],
            1000,
            500,
            timestamp=1.0,
        )

        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].class_name, "chair")
        self.assertEqual(warnings[0].zone, "center")
        self.assertFalse(warnings[0].approaching)

    def test_detects_approach_across_multiple_fast_frames(self):
        self.analyzer.analyze(
            [track("car", 1, [480, 225, 520, 275])],
            1000,
            500,
            timestamp=1.0,
        )
        self.analyzer.analyze(
            [track("car", 1, [390, 190, 610, 310])],
            1000,
            500,
            timestamp=1.1,
        )
        warnings = self.analyzer.analyze(
            [track("car", 1, [375, 175, 625, 325])],
            1000,
            500,
            timestamp=1.3,
        )

        self.assertEqual(len(warnings), 1)
        self.assertTrue(warnings[0].approaching)
        self.assertIn(
            "അതിവേഗം അടുത്തുവരുന്നു",
            format_threat_warning_in_malayalam(
                warnings[0].class_name, warnings[0].zone, warnings[0].approaching
            ),
        )

    def test_flags_rapidly_approaching_obstacle_on_side(self):
        self.analyzer.analyze(
            [track("bicycle", 1, [50, 250, 150, 350])],
            1000,
            500,
            timestamp=2.0,
        )
        warnings = self.analyzer.analyze(
            [track("bicycle", 1, [25, 200, 175, 400])],
            1000,
            500,
            timestamp=2.5,
        )

        self.assertEqual(warnings[0].zone, "left")
        self.assertTrue(warnings[0].approaching)

    def test_sorts_urgent_warnings_by_priority(self):
        warnings = self.analyzer.analyze(
            [
                track("chair", 1, [400, 250, 600, 490]),
                track("stairs", 1, [400, 250, 600, 490]),
                track("car", 1, [400, 250, 600, 490]),
            ],
            1000,
            500,
            timestamp=3.0,
        )

        self.assertEqual(
            [warning.class_name for warning in warnings],
            ["stairs", "car", "chair"],
        )

    def test_clears_history_for_tracks_missing_from_current_frame(self):
        self.analyzer.analyze(
            [track("car", 1, [400, 200, 600, 300])],
            1000,
            500,
            timestamp=1.0,
        )
        self.analyzer.analyze([], 1000, 500, timestamp=1.1)
        warnings = self.analyzer.analyze(
            [track("car", 1, [450, 200, 550, 300])],
            1000,
            500,
            timestamp=1.3,
        )

        self.assertFalse(warnings)

    def test_road_hazards_prioritizes_ditch_over_stairs_and_vehicles(self):
        warnings = self.analyzer.analyze(
            [
                track("car", 1, [400, 250, 600, 490]),
                track("ditch", 2, [50, 250, 250, 490]),
                track("stairs", 3, [400, 250, 600, 490]),
            ],
            1000,
            500,
            timestamp=4.0,
        )

        self.assertEqual(warnings[0].class_name, "ditch")
        self.assertEqual(warnings[0].zone, "left")
        self.assertIn("ഓടയുണ്ട്", format_threat_warning_in_malayalam(
            warnings[0].class_name, warnings[0].zone, warnings[0].approaching
        ))

    def test_road_hazards_detects_pothole_in_walking_path(self):
        warnings = self.analyzer.analyze(
            [
                track("pothole", 1, [450, 300, 550, 420]),
            ],
            1000,
            500,
            timestamp=5.0,
        )

        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].class_name, "pothole")
        self.assertEqual(warnings[0].zone, "center")
        self.assertIn("കുഴിയുണ്ട്", format_threat_warning_in_malayalam(
            warnings[0].class_name, warnings[0].zone, warnings[0].approaching
        ))

    def test_road_hazards_detects_puddle_in_path(self):
        warnings = self.analyzer.analyze(
            [
                track("puddle", 1, [420, 320, 580, 450]),
            ],
            1000,
            500,
            timestamp=6.0,
        )

        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].class_name, "puddle")
        self.assertIn("വെള്ളക്കെട്ടുണ്ട്", format_threat_warning_in_malayalam(
            warnings[0].class_name, warnings[0].zone, warnings[0].approaching
        ))

    def test_detect_road_hazards_from_frame(self):
        import numpy as np
        # Create a synthetic frame with road and ditch edge
        frame = np.ones((500, 1000, 3), dtype=np.uint8) * 120
        # Draw high-contrast ditch edge lines on left side
        frame[250:, :300] = 30 # dark ditch/canal
        frame[250:, 50:55] = 255 # sharp edge

        warnings = self.analyzer.analyze(
            [],
            1000,
            500,
            timestamp=7.0,
            frame=frame,
        )

        self.assertTrue(any(w.class_name == "ditch" for w in warnings))


    def test_rejects_invalid_frame_dimensions(self):
        with self.assertRaises(ValueError):
            self.analyzer.analyze([], 0, 500, timestamp=1.0)


if __name__ == "__main__":
    unittest.main()


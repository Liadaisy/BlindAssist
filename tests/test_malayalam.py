import unittest

from modules.malayalam import (
    describe_scene_in_malayalam,
    format_threat_warning_in_malayalam,
)


class MalayalamDescriptionTests(unittest.TestCase):
    def test_translates_object_count_position_motion_and_new_detection(self):
        result = describe_scene_in_malayalam(
            [("person", 1), ("car", 2)],
            [("person", "left")],
            [("car", "right")],
            ["car"],
        )

        self.assertIn("ഒരു വ്യക്തി", result)
        self.assertIn("രണ്ട് കാറുകൾ", result)
        self.assertIn("ഇടതുവശത്ത്", result)
        self.assertIn("വലത്തേക്ക് നീങ്ങുന്നു", result)
        self.assertIn("പുതുതായി കണ്ടെത്തിയത്", result)

    def test_translates_road_hazards_in_scene(self):
        result = describe_scene_in_malayalam(
            [("pothole", 1), ("puddle", 2)],
            [("pothole", "center"), ("puddle", "right")],
            [],
            ["pothole"],
        )

        self.assertIn("ഒരു കുഴി", result)
        self.assertIn("രണ്ട് വെള്ളക്കെട്ടുകൾ", result)

    def test_formats_road_hazard_warnings(self):
        ditch_msg = format_threat_warning_in_malayalam("ditch", "left", False)
        self.assertIn("ഓടയുണ്ട്", ditch_msg)
        self.assertIn("അരികിലേക്ക് പോകരുത്", ditch_msg)

        pothole_msg = format_threat_warning_in_malayalam("pothole", "center", False)
        self.assertIn("കുഴിയുണ്ട്", pothole_msg)
        self.assertIn("ശ്രദ്ധിച്ചു നടക്കുക", pothole_msg)

        puddle_msg = format_threat_warning_in_malayalam("puddle", "right", False)
        self.assertIn("വെള്ളക്കെട്ടുണ്ട്", puddle_msg)

    def test_reports_empty_scene_in_malayalam(self):
        self.assertEqual(
            describe_scene_in_malayalam([], [], [], []),
            "ഫ്രെയിമിൽ ഇപ്പോൾ വസ്തുക്കളൊന്നും കണ്ടെത്തിയില്ല.",
        )

    def test_preserves_unrecognized_detector_labels(self):
        result = describe_scene_in_malayalam(
            [("wheelchair", 1)], [], [], []
        )

        self.assertIn("wheelchair", result)


if __name__ == "__main__":
    unittest.main()


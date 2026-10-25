import unittest
from modules.speaker import Speaker


class SpeakerTests(unittest.TestCase):
    def setUp(self):
        self.speaker = Speaker()

    def test_malayalam_voice_is_available(self):
        self.assertTrue(self.speaker.has_malayalam_voice())

    def test_speak_malayalam_enqueues_safely(self):
        # Should enqueue without throwing exceptions
        self.speaker.speak_malayalam("ശ്രദ്ധിക്കുക. റോഡിൽ കുഴിയുണ്ട്.")


if __name__ == "__main__":
    unittest.main()

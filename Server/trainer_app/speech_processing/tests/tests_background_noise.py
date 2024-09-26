import os
import sys
import unittest

sys.path.append('..')
from automatic_speech_recognition import AutomaticSpeechRecognition
from background_noise import BackgroundNoise


class BackgroundNoiseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.abspath(os.path.dirname(__file__))
        test_path = os.path.abspath(os.path.join(path, "long_rus.wav"))
        ASR = AutomaticSpeechRecognition(test_path)
        _, word_arrays, _ = ASR.get_speech_recognition()
        cls.background_noise_long = BackgroundNoise(word_arrays[1])

        test_path = os.path.abspath(os.path.join(path, "1.wav"))
        ASR = AutomaticSpeechRecognition(test_path)
        _, word_arrays, _ = ASR.get_speech_recognition()
        cls.background_noise_short = BackgroundNoise(word_arrays[1])

    def test_long(self):
        timestamps = self.background_noise_long.get_high_noise_timestamps()
        self.assertIsNotNone(timestamps)
        self.assertGreater(len(timestamps), 0)
        for period in timestamps:
            self.assertEqual(len(period), 2)
            self.assertGreater(period[1], period[0])

    def test_short(self):
        timestamps = self.background_noise_short.get_high_noise_timestamps()
        self.assertEqual(len(timestamps), 0)
        self.assertEqual(timestamps, [])

    def test_params(self):
        noise_time_window = \
            self.background_noise_long.params["noise_time_window"]
        self.assertEqual(noise_time_window, 30)
        noise_percentage = \
            self.background_noise_long.params["noise_percentage"]
        self.assertEqual(noise_percentage, 0.45)


if __name__ == '__main__':
    unittest.main()

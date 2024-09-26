import math
import os
import sys
import unittest
from moviepy.audio.io.AudioFileClip import AudioFileClip

sys.path.append('..')
from automatic_speech_recognition import AutomaticSpeechRecognition
from intelligibility import Intelligibility


class IntelligibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.abspath(os.path.dirname(__file__))
        test_path = os.path.abspath(os.path.join(path, "long_rus.wav"))
        analyzed_segment_len = 10
        clip = AudioFileClip(test_path)
        duration = clip.duration
        ASR = AutomaticSpeechRecognition(test_path)
        cleaned_transcription, word_arrays, correct_transcription =\
            ASR.get_speech_recognition()
        all_words_without_noise, noise = word_arrays
        cls.intelligibility = Intelligibility(
            test_path, all_words_without_noise,
            noise, analyzed_segment_len=analyzed_segment_len)
        cls.number_of_segments = math.ceil(duration / analyzed_segment_len)

    def test_stoi_index(self):
        indexes = self.intelligibility.stoi_index()
        self.assertIsNotNone(indexes)
        self.assertEqual(len(indexes), self.number_of_segments)
        for index in indexes:
            self.assertGreaterEqual(1, index)
            self.assertGreaterEqual(index, 0)

    def test_indirect_features(self):
        fast_intervals, noisy_intervals = \
            self.intelligibility.indirect_features()
        self.assertIsNotNone(fast_intervals)
        self.assertIsNotNone(noisy_intervals)
        self.assertEqual(len(fast_intervals), 0)
        self.assertGreater(len(noisy_intervals), 0)
        for interval in noisy_intervals:
            self.assertGreater(interval[1], interval[0])

    def test_get_intelligibility_features(self):
        indexes, fast_intervals, noisy_intervals = \
            self.intelligibility.get_intelligibility_features()
        self.assertEqual(len(indexes), self.number_of_segments)
        for index in indexes:
            self.assertGreaterEqual(1, index)
            self.assertGreaterEqual(index, 0)
        self.assertEqual(fast_intervals, [])
        self.assertGreater(len(noisy_intervals), 0)
        for interval in noisy_intervals:
            self.assertGreater(interval[1], interval[0])


if __name__ == '__main__':
    unittest.main()

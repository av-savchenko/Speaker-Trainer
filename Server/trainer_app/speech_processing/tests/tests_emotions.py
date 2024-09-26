import math
import os
import sys
import unittest
from moviepy.audio.io.AudioFileClip import AudioFileClip

sys.path.append('..')
from emotions import AudioEmotions


class AudioEmotionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.abspath(os.path.dirname(__file__))
        test_path = os.path.abspath(os.path.join(path, "long_rus.wav"))
        analyzed_segment_len = 10
        cls.emotions = AudioEmotions(
            test_path,
            analyzed_segment_len=analyzed_segment_len,
            negative_emotions=[False, True, True, False, False, False])
        clip = AudioFileClip(test_path)
        cls.number_of_segments = math.ceil(clip.duration / analyzed_segment_len)

    def test_emotions_analysis(self):
        self.assertEqual(self.number_of_segments, 59)
        negative_emotions_percentage, neutral_emotion_percentage = self.emotions.emotions_analysis()
        self.assertIsNotNone(negative_emotions_percentage)
        self.assertIsNotNone(neutral_emotion_percentage)
        self.assertEqual(len(negative_emotions_percentage), self.number_of_segments)
        self.assertEqual(len(neutral_emotion_percentage), self.number_of_segments)
        for percentage in negative_emotions_percentage:
            self.assertGreaterEqual(1, percentage)
            self.assertGreaterEqual(percentage, 0)
        for percentage in neutral_emotion_percentage:
            self.assertGreaterEqual(1, percentage)
            self.assertGreaterEqual(percentage, 0)


if __name__ == '__main__':
    unittest.main()

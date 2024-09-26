import math
import os
import sys
import unittest
import numpy as np
from moviepy.audio.io.AudioFileClip import AudioFileClip

sys.path.append('..')
from speech_processing_subsystem import SpeechProcessingSubsystem


class SpeechProcessingSubsystemTest(unittest.TestCase):
    speech_processing_subsystem = None

    @classmethod
    def setUpClass(cls):
        path = os.path.abspath(os.path.dirname(__file__))
        test_path = os.path.abspath(os.path.join(path, "long_video.mkv"))
        analyzed_segment_len = 10
        clip = AudioFileClip(test_path)
        duration = clip.duration
        cls.speech_processing_subsystem = SpeechProcessingSubsystem(
            test_path, [False, True, True, False, False, False],
            analyzed_segment_len=analyzed_segment_len)
        cls.number_of_segments = math.ceil(duration / analyzed_segment_len)
        cls.speech_processing_subsystem.speech_recognition()

    def test_get_emotionality(self):
        negative_emotions_fractions, neutral_emotion_fractions = \
            self.speech_processing_subsystem.get_emotionality()
        self.assertIsNotNone(negative_emotions_fractions)
        self.assertIsNotNone(neutral_emotion_fractions)
        self.assertEqual(len(negative_emotions_fractions), self.number_of_segments)
        self.assertEqual(len(neutral_emotion_fractions), self.number_of_segments)
        for i, j in zip(negative_emotions_fractions, neutral_emotion_fractions):
            self.assertGreaterEqual(1, i)
            self.assertGreaterEqual(1, j)
            self.assertGreaterEqual(i, 0)
            self.assertGreaterEqual(j, 0)

    def test_get_filler_words(self):
        all_filler_words_dict, worst_words = \
            self.speech_processing_subsystem.get_filler_words()
        self.assertIsNotNone(all_filler_words_dict)
        self.assertIsNotNone(worst_words)
        self.assertEqual(len(all_filler_words_dict), 6)
        self.assertEqual(len(worst_words), 2)
        self.assertEqual(worst_words["в общем"], 5)
        self.assertEqual(worst_words["ну"], 6)

    def test_get_speech_rate(self):
        intervals, fractions, fraction = self.\
            speech_processing_subsystem.get_speech_rate()
        self.assertIsNotNone(intervals)
        self.assertIsNotNone(fractions)
        self.assertEqual(len(fractions), self.number_of_segments)
        for frac in fractions:
            self.assertGreaterEqual(1, frac)
            self.assertGreaterEqual(frac, 0)
        self.assertIsNotNone(fraction)
        self.assertGreater(1, fraction)
        self.assertGreater(fraction, 0)
        self.assertEqual(
            round(np.average(fractions), 2), round(fraction, 2))

    def test_get_background_noise(self):
        high_noise_intervals, fractions, fraction = \
            self.speech_processing_subsystem.get_background_noise()
        self.assertIsNotNone(high_noise_intervals)
        self.assertIsNotNone(fractions)
        self.assertEqual(len(fractions), self.number_of_segments)
        self.assertIsNotNone(fraction)
        for frac in fractions:
            self.assertGreaterEqual(1, frac)
            self.assertGreaterEqual(frac, 0)
        self.assertGreaterEqual(1, fraction)
        self.assertGreaterEqual(fraction, 0)

    def test_get_intelligibility(self):
        negative_fractions, negative_fraction = \
            self.speech_processing_subsystem.get_intelligibility()
        self.assertIsNotNone(negative_fractions)
        self.assertIsNotNone(negative_fraction)
        self.assertEqual(len(negative_fractions), self.number_of_segments)
        for frac in negative_fractions:
            self.assertGreaterEqual(1, frac)
            self.assertGreaterEqual(frac, 0)
        self.assertGreater(1, negative_fraction)
        self.assertGreater(negative_fraction, 0)
        self.assertEqual(round(np.average(negative_fractions), 2),
                         round(negative_fraction, 2))

    def test_speech_recognition(self):
        self.assertIsNotNone(self.speech_processing_subsystem.cleaned_transcription)
        self.assertIsNotNone(self.speech_processing_subsystem.all_words_without_noise)
        self.assertIsNotNone(self.speech_processing_subsystem.noise)

    def test_get_fractions_from_intervals(self):
        intervals = [[1.0, 12.0]]
        fractions = self.speech_processing_subsystem.\
            get_fractions_from_intervals(intervals)
        self.assertIsNotNone(fractions)
        self.assertEqual(len(fractions), self.number_of_segments)
        self.assertEqual(fractions[0], 0.9)
        self.assertEqual(fractions[1], 0.2)
        for i in fractions[2:]:
            self.assertEqual(i, 0.)

    def test_unite_intervals(self):
        intervals_1 = [[1.0, 5.0], [7.0, 10.0], [15.0, 18.0], [20.0, 22.0]]
        intervals_2 = [[1.0, 4.0], [6.0, 10.0], [17.0, 21.0]]
        united = self.speech_processing_subsystem.unite_intervals(intervals_1, intervals_2)
        self.assertIsNotNone(united)
        self.assertEqual(united, [[1.0, 4.0], [7.0, 10.0], [17.0, 18.0], [20.0, 21.0]])

    def test_periods_to_fractions(self):
        intervals = [[1.0, 5.0], [7.0, 10.0], [15.0, 18.0], [20.0, 22.0]]
        fractions = self.speech_processing_subsystem.periods_to_fractions(intervals, 4)
        self.assertIsNotNone(fractions)
        answers = [0.7, 0.3, 0.2, 0.]
        for i, j in zip(fractions, answers):
            self.assertEqual(i, j)

    def test_get_fraction(self):
        intervals = [[1.0, 5.0], [7.0, 10.0], [15.0, 18.0], [20.0, 22.0]]
        fraction = self.speech_processing_subsystem.get_fraction(intervals)
        self.assertIsNotNone(fraction)
        self.assertEqual(round(fraction, 3), round(12 / self.speech_processing_subsystem.duration, 3))


if __name__ == '__main__':
    unittest.main()

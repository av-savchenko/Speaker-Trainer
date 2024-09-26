import os
import sys
import unittest

sys.path.append('..')
from automatic_speech_recognition import AutomaticSpeechRecognition
from speech_rate import SpeechRate


class SpeechRateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.abspath(os.path.dirname(__file__))
        test_path = os.path.abspath(os.path.join(path, "long_rus.wav"))
        ASR = AutomaticSpeechRecognition(test_path)
        _, word_arrays, _ = ASR.get_speech_recognition()
        cls.speech_rate = SpeechRate(word_arrays[0])

    def test_find_pause_intervals(self):
        pauses = self.speech_rate.find_pauses()
        intervals = self.speech_rate.find_pause_intervals(pauses)
        self.assertGreater(len(intervals), 0)
        for interval in intervals:
            self.assertGreater(interval[1], interval[0])

    def test_find_incorrect_speech_rate_intervals(self):
        slow_intervals, fast_intervals = self.speech_rate.find_incorrect_speech_rate_intervals()
        self.assertEqual(len(fast_intervals), 0)
        self.assertGreater(len(slow_intervals), 0)
        for interval in slow_intervals:
            self.assertGreater(interval[1], interval[0])

    def test_unite_slow_speech_rate_intervals(self):
        final_intervals = self.speech_rate.unite_slow_speech_rate_intervals()
        self.assertGreater(len(final_intervals), 0)
        for interval in final_intervals:
            self.assertGreater(interval[1], interval[0])

    def test_find_pauses(self):
        pauses = self.speech_rate.find_pauses()
        self.assertIsNotNone(pauses)
        self.assertGreater(len(pauses), 0)
        for pause in pauses:
            self.assertGreater(pause[1], pause[0])


if __name__ == '__main__':
    unittest.main()

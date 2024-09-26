import os
import sys
import unittest

sys.path.append('..')
from automatic_speech_recognition import AutomaticSpeechRecognition


class AutomaticSpeechRecognitionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.abspath(os.path.dirname(__file__))
        test_path = os.path.abspath(os.path.join(path, "1.wav"))
        cls.ASR = AutomaticSpeechRecognition(test_path)

    def test(self):
        cleaned_transcription, word_arrays, correct_transcription = self.ASR.get_speech_recognition()
        self.assertEqual(correct_transcription, True)
        self.assertIsNotNone(cleaned_transcription)
        for sign in [".", ",", "!", "?", "-"]:
            self.assertEqual(cleaned_transcription.find(sign), -1)
        self.assertIsNotNone(word_arrays)
        self.assertEqual(len(word_arrays), 2)
        self.assertGreater(len(word_arrays[0]), 0)
        for word in word_arrays[0]:
            for key in ["text", "start", "end"]:
                self.assertEqual(key in word, True)
        self.assertGreater(len(word_arrays[1]), 0)
        for interval in word_arrays[1]:
            self.assertGreater(interval[1], interval[0])
        self.assertEqual(correct_transcription, True)


if __name__ == '__main__':
    unittest.main()

import os
import sys
import unittest

sys.path.append('..')
from automatic_speech_recognition import AutomaticSpeechRecognition
from filler_words import FillerWordsAndPhrases


class FillerWordsAndPhrasesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.abspath(os.path.dirname(__file__))
        test_path = os.path.abspath(os.path.join(path, "long_rus.wav"))
        cleaned_transcription, _, _ = \
            AutomaticSpeechRecognition(test_path).get_speech_recognition()
        cls.filler_words = FillerWordsAndPhrases(cleaned_transcription)

    def test_count_occurrences(self):
        phrases, phrases_from_list = self.filler_words.count_occurrences()
        self.assertIsNotNone(phrases)
        self.assertEqual(phrases[0], ("в общем", 5))
        self.assertIsNotNone(phrases_from_list)
        self.assertEqual(phrases_from_list["в общем"], 5)

    def test_find_worst_phrases(self):
        phrases, _ = self.filler_words.count_occurrences()
        self.assertIsNotNone(phrases)
        worst_word_pairs = self.filler_words.find_worst_phrases(phrases)
        self.assertIsNotNone(worst_word_pairs)
        self.assertEqual(worst_word_pairs["в общем"], 5)

    def test_get_one_words(self):
        fdist = self.filler_words.get_one_words()
        self.assertIsNotNone(fdist.most_common)
        self.assertIsNotNone(fdist.most_common(1)[0], ("ну", 7))

    def test_find_worst_words(self):
        fdist = self.filler_words.get_one_words()
        self.assertIsNotNone(fdist)
        worst_words = self.filler_words.find_worst_words(fdist)
        self.assertIsNotNone(worst_words)
        self.assertEqual(worst_words["ну"], 7)

    def test_get_filler_words_final(self):
        total_dict, worst_dict = \
            self.filler_words.get_filler_words_final()
        self.assertIsNotNone(total_dict)
        self.assertIsNotNone(worst_dict)
        self.assertEqual(len(worst_dict), 2)
        self.assertEqual(worst_dict["ну"], 7)
        self.assertEqual(worst_dict["в общем"], 5)

    def test_params(self):
        word_count_multiplier = self.filler_words.params["word_count_multiplier"]
        self.assertEqual(word_count_multiplier, 0.1)
        occurrence_percentage = self.filler_words.params["occurrence_percentage"]
        self.assertEqual(occurrence_percentage, 0.0001)


if __name__ == '__main__':
    unittest.main()

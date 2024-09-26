import os
import joblib
import string
import moviepy.editor as mp_editor
import whisper_timestamped


class AutomaticSpeechRecognition:
    """
    Class for transcribing audio into text.
    Creates speech text, words time intervals, unidentified noise time intervals.
    """
    def __init__(self, path):
        """
        Initialization of speech processing class
        @param path: path to audio file
        """
        clip = mp_editor.AudioFileClip(path)
        self.path = path
        self.duration = clip.duration
        self.transcription = None

    def get_speech_recognition(self):
        """
        Translates audio to text, creates words lists with timestamps (with and without background noise)
        """
        path = os.path.abspath(os.path.dirname(__file__))
        ASR_model_path = os.path.abspath(os.path.join(path, "whisper_model.sav"))
        model = joblib.load(open(ASR_model_path, 'rb'))
        # whisper timestamped allows to receive timestamps for each word and sentence, as well as
        # noise timestamps
        audio = whisper_timestamped.load_audio(self.path)
        self.transcription = whisper_timestamped.transcribe(
            model,
            audio,
            language="ru",
            detect_disfluencies=True,
            remove_punctuation_from_words=False)
        correct_transcription = self.check_transcription()
        # creation of transcription without punctuation marks
        transcription = self.transcription["text"].lower()
        transcription = transcription.translate(str.maketrans('', '', string.punctuation))
        transcription = "".join([ch for ch in transcription if ch not in string.digits])
        cleaned_transcription = " ".join(transcription.split())
        word_arrays = self.get_words()
        return cleaned_transcription, word_arrays, correct_transcription

    def check_transcription(self):
        """
        Checks if transcription is correct (if there are word doubles at the end of transcription)
        @return: True if transcription is correct, False otherwise
        """
        words = self.transcription["text"].split()
        segments = self.transcription["segments"]
        end_idx = len(segments)
        # find first segment out of time range
        for i in range(len(segments)):
            if segments[i]["end"] > self.duration:
                end_idx = i
                break
        # checks if there is no segments out of time range
        if end_idx == len(segments):
            return True
        else:
            # count words out of time range
            extra_words = 0
            for i in range(end_idx, len(segments)):
                extra_words += len(segments[i]["text"].split())
            # transcription correction
            self.transcription["text"] = " ".join((self.transcription["text"].split())[:len(words) - extra_words])
            self.transcription["segments"] = self.transcription["segments"][:end_idx]
            return False

    def get_words(self):
        """
        Creates lists with all words (with background noise), words without noise and only noise
        @return: three lists with dicts of words and their timestamps
        """
        all_words, all_words_without_noise, noise = [], [], []
        for sentence in self.transcription["segments"]:
            for word in sentence["words"]:
                all_words.append(word)
                if word["text"] != "[*]":
                    all_words_without_noise.append(word)
                else:
                    noise.append((word["start"], word["end"]))
        return all_words_without_noise, noise

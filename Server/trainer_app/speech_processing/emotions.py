import math
import os

import joblib
import numpy as np
from aniemore.models import HuggingFaceModel
from aniemore.recognizers.voice import VoiceRecognizer
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pydub import AudioSegment
from tqdm import tqdm
import wave


class AudioEmotions:
    """
    Class for emotions detecting.
    Counts percentage of preferred emotions and percentage of neutral emotion.
    """
    def __init__(self, path, analyzed_segment_len, negative_emotions):
        """
        Initialization of emotion classification class
        @param path: path to audio file
        @param analyzed_segment_len: length of file segment to analyze separately
        @param negative_emotions: list of preferred emotions
        """
        self.path = path
        self.analyzed_segment_len = analyzed_segment_len
        self.negative_emotions = negative_emotions
        # paths for N-second sub clips
        path = os.path.abspath(os.path.dirname(__file__))
        self.subclip_path = os.path.abspath(os.path.join(path, "file_processing/processing.wav"))
        self.subclip_modified_path = os.path.abspath(os.path.join(path, "file_processing/processing2.wav"))
        # order of emotions in model
        self.order = ["happiness", "anger", "disgust", "neutral", "sadness", "enthusiasm"]

    def emotions_analysis(self):
        """
        Analyzes speech per N seconds (see init params) and provides emotions probabilities
        @return: lists with emotions probabilities
        """
        #model = VoiceRecognizer(model=HuggingFaceModel.Voice.Wav2Vec2)
        path = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(path, "audio_emotion_recognition_model.sav"))
        model = joblib.load(open(model_path, 'rb'))
        clip = AudioFileClip(self.path)
        duration = clip.duration
        # number of file fragments to analyze
        number_of_segments = math.ceil(duration / self.analyzed_segment_len)
        negative_emotions_percentage = np.zeros(number_of_segments)
        neutral_emotion_percentage = np.zeros(number_of_segments)
        time = self.analyzed_segment_len
        for i in tqdm(range(number_of_segments)):
            # path to analyzed file fragment
            subclip = clip.subclip(i * time, min(i * time + time, duration))
            subclip.write_audiofile(self.subclip_path, logger=None)

            # sub clip preprocessing to convert stereo to mono
            self.audio_channels_processing()
            emotions_percentages = model.recognize(self.subclip_modified_path, return_single_label=False)
            # counting of preferred emotions percentage
            for idx, emotion in enumerate(self.order):
                if self.negative_emotions[idx]:
                    negative_emotions_percentage[i] += emotions_percentages[emotion]
                neutral_emotion_percentage[i] = emotions_percentages["neutral"]

        # deleting of intermediate files
        file_paths = [self.subclip_path, self.subclip_modified_path]
        for file_path in file_paths:
            if os.path.isfile(file_path):
                os.remove(file_path)
        return negative_emotions_percentage, neutral_emotion_percentage

    def audio_channels_processing(self):
        """
        Rewriting file to one channel if necessary
        """
        audio_file = wave.open(self.subclip_path)
        channels = audio_file.getnchannels()
        sound = AudioSegment.from_wav(self.subclip_path)
        if channels > 1:
            sound = sound.set_channels(1)
        # rewriting one channel file
        sound.export(self.subclip_modified_path, format="wav")

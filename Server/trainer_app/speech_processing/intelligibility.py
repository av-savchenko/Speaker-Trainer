import math
import os
import noisereduce as nr
import librosa
import numpy as np
import scipy.io.wavfile as wavf
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pystoi import stoi

from .speech_rate import *
from .background_noise import *


class Intelligibility:
    """
    Class for intelligibility detecting.
    Uses info from background noise analysis and high speech rate timestamps.
    """
    def __init__(self, path, all_words_without_noise, noise, analyzed_segment_len):
        """
        Initialization of background noise analysis class
        @param path: path to audio file
        @param all_words_without_noise: list of all words and their timestamps
        @param noise: timestamps with background noise, list of two-element lists
        @param analyzed_segment_len: length of file segment to analyze separately
        """
        self.noise = noise
        self.path = path
        self.all_words_without_noise = all_words_without_noise
        self.analyzed_segment_len = analyzed_segment_len

    def stoi_index(self):
        """
        Counting short time objective intelligibility index per file fragment
        @return: list with STOI indexes for each fragment
        """
        # paths for file fragments
        path = os.path.abspath(os.path.dirname(__file__))
        subclip_path = os.path.abspath(os.path.join(path, "file_processing/processing.wav"))
        subclip_modified_path = os.path.abspath(os.path.join(path, "file_processing/processing2.wav"))

        clip = AudioFileClip(self.path)
        duration = clip.duration
        # number of file segments to analyze
        number_of_segments = math.ceil(duration / self.analyzed_segment_len)
        indexes = np.zeros(number_of_segments)
        for i in range(number_of_segments):
            # file fragment (checks for len not out of file length)
            subclip = clip.subclip(i * self.analyzed_segment_len,
                                   min((i + 1) * self.analyzed_segment_len, clip.duration))
            # it is ineffective to analyze too short fragments
            if subclip.duration < 3:
                indexes[i] = 0.5
                continue
            subclip.write_audiofile(subclip_path, logger=None)
            data, rate = librosa.load(subclip_path)
            # cleaning degraded speech signal
            reduced_noise = nr.reduce_noise(y=data, sr=rate, thresh_n_mult_nonstationary=2, stationary=False)
            wavf.write(subclip_modified_path, rate, reduced_noise)
            # loading signal info
            clean, fs = librosa.load(subclip_modified_path)
            base, fs = librosa.load(subclip_path)
            # counting and saving STOI indexes
            index = stoi(clean, base, fs, extended=False)
            indexes[i] = round(index, 3)

        # deleting intermediate files
        file_paths = [subclip_path, subclip_modified_path]
        for file_path in file_paths:
            if os.path.isfile(file_path):
                os.remove(file_path)
        return indexes

    def indirect_features(self):
        """
        Analyses intelligibility of speech
        @return: intervals with high speech and high levels of background noise
        """
        # timestamps with fast speech rate
        speech_rate = SpeechRate(self.all_words_without_noise)
        _, fast_intervals = speech_rate.find_incorrect_speech_rate_intervals()
        # timestapms with high background noise
        noisy_intervals = BackgroundNoise(self.noise).get_high_noise_timestamps()

        return fast_intervals, noisy_intervals

    def get_intelligibility_features(self):
        """
        Final method for aggregating file info
        @return: lists with STOI indexes, intervals with high speech and high levels of background noise
        """
        indexes = self.stoi_index()
        fast_intervals, noisy_intervals = self.indirect_features()
        return indexes, fast_intervals, noisy_intervals

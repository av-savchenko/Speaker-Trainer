import logging

from .filler_words import *
from .background_noise import *
from .speech_rate import *
from .emotions import *
from .automatic_speech_recognition import *
from .intelligibility import *

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('PIL.Image').setLevel(logging.WARNING)
logging.getLogger('whisper_timestamped').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class SpeechProcessingSubsystem:
    def __init__(self, path, negative_emotions_bool, analyzed_segment_len):
        """
        Initialization of speech processing class
        @param path: path to video file
        @param negative_emotions_bool: list of unwanted emotions (set by user)
        @param analyzed_segment_len: length of file segment to analyze separately
        """
        # rewrite video to audio file
        clip = mp_editor.VideoFileClip(path)
        audio_path = path[:path.rfind('.')] + '.wav'
        clip.audio.write_audiofile(audio_path, logger=None)
        self.path = audio_path
        # fields for words and noise timestamps
        self.cleaned_transcription = None
        self.all_words_without_noise = None
        self.noise = None
        self.duration = clip.duration
        self.analyzed_segment_len = analyzed_segment_len
        self.negative_emotions_bool = negative_emotions_bool
        logger.debug("File path: " + str(self.path))
        logger.debug("File duration: " + str(self.duration))

    def speech_recognition(self):
        """
        Performs ASR process
        """
        speech_recogniser = AutomaticSpeechRecognition(self.path)
        cleaned_transcription, word_arrays, correct_transcription = \
            speech_recogniser.get_speech_recognition()
        # fill class params with ASR results
        self.cleaned_transcription = cleaned_transcription
        self.all_words_without_noise = word_arrays[0]
        self.noise = word_arrays[1]
        if correct_transcription:
            logger.debug("Correct transcription")

    @staticmethod
    def unite_intervals(intervals_1, intervals_2):
        """
        Unite two time frames intervals
        @param intervals_1: first list of intervals
        @param intervals_2: second list of intervals
        @return: united list of intervals
        """
        final_intervals = []
        # indexes to indexing through lists
        first_idx, second_idx = 0, 0
        while first_idx < len(intervals_1) and second_idx < len(intervals_2):
            interval_1_start, interval_1_end = intervals_1[first_idx]
            interval_2_start, interval_2_end = intervals_2[second_idx][0], intervals_2[second_idx][1]
            # if first interval's time period is earlier
            if interval_1_start <= interval_2_start:
                # first interval's time period is inside second's
                if interval_1_end <= interval_2_start:
                    first_idx += 1
                elif interval_2_start < interval_1_end <= interval_2_end:
                    final_intervals.append([interval_2_start, interval_1_end])
                    first_idx += 1
                else:
                    final_intervals.append([interval_2_start, interval_2_end])
                    second_idx += 1
            # if second interval's time period is earlier
            elif interval_2_start <= interval_1_start <= interval_2_end:
                if interval_1_end <= interval_2_end:
                    final_intervals.append([interval_1_start, interval_1_end])
                    first_idx += 1
                else:
                    final_intervals.append([interval_1_start, interval_2_end])
                    second_idx += 1
            else:
                second_idx += 1
        return final_intervals

    def periods_to_fractions(self, intervals, length):
        """
        Saves percentages of intervals per analyzed file fragment length
        @param intervals: time intervals of any kind
        @param length: result's list length
        @return: list with fractions (percentages) of occurrence
        """
        res = np.zeros(length)
        for i in intervals:
            fraction = (i[1] - i[0]) / self.analyzed_segment_len
            idx = int(i[0] // self.analyzed_segment_len)
            res[idx] = round(res[idx] + fraction, 3)
        return res

    def get_fraction(self, timestamps):
        """
        Counts timestamps proportion of some event
        @param timestamps: time periods of some event
        @return: timestamps proportion of some event
        """
        duration = 0
        for time_period in timestamps:
            duration += time_period[1] - time_period[0]
        return duration / self.duration

    def get_fractions_from_intervals(self, intervals):
        """
        Transform random length intervals to N-second fractions
        @param intervals: intervals of some event
        @return: list of fraction per file fragment
        """
        length = math.ceil(self.duration / self.analyzed_segment_len)
        fixed_intervals = [[i * self.analyzed_segment_len, (i + 1) * self.analyzed_segment_len] for i in range(length)]
        united_intervals = self.unite_intervals(intervals, fixed_intervals)
        fractions = self.periods_to_fractions(united_intervals, len(fixed_intervals))
        return fractions

    def get_emotionality(self):
        """
        Analyses emotionality of file
        @return: list of lists of emotions probabilities and time period per which emotions are defined
        """
        audio_emotions = AudioEmotions(self.path, self.analyzed_segment_len, self.negative_emotions_bool)
        negative_emotions_fractions, neutral_emotion_fractions = audio_emotions.emotions_analysis()
        return negative_emotions_fractions, neutral_emotion_fractions

    def get_filler_words(self):
        """
        Analyses presence of filler words
        @return: dicts with all filler words and phrases and with most common ones
        """
        filler_words = FillerWordsAndPhrases(self.cleaned_transcription)
        all_filler_words_dict, worst_words = filler_words.get_filler_words_final()
        logger.debug("All filler words: " + str(all_filler_words_dict))
        logger.debug("Worst words: " + str(worst_words))
        return all_filler_words_dict, worst_words

    def get_speech_rate(self):
        """
        Analyses speech rate of speech
        @return: intervals with slow speech rate and their percentage of file duration
        """
        speech_rate = SpeechRate(self.all_words_without_noise)
        speech_rate_results, pause_intervals = speech_rate.get_intervals()
        intervals = self.unite_intervals(speech_rate_results, pause_intervals)
        logger.debug("Pauses intervals: " + str(intervals))
        fractions = self.get_fractions_from_intervals(intervals)
        return intervals, fractions, self.get_fraction(intervals)

    def get_background_noise(self):
        """
        Analyses background noise presence
        @return: intervals with high background noise and their percentage of file duration
        """
        # collect high background noise intervals
        background_noise = BackgroundNoise(self.noise)
        high_noise_intervals = background_noise.get_high_noise_timestamps()
        logger.debug("Background_noise intervals: " + str(high_noise_intervals))
        logger.debug("Background_noise fraction: " + str(self.get_fraction(high_noise_intervals)))
        # transform to fractions for each file fragment
        high_noise_fractions = self.get_fractions_from_intervals(high_noise_intervals)
        high_noise_fractions = np.array(high_noise_fractions)

        # collect STOI indexes
        intelligibility = Intelligibility(self.path, self.all_words_without_noise, self.noise,
                                          self.analyzed_segment_len)
        indexes = intelligibility.stoi_index()
        # transform to fractions for each file fragment
        fractions = (high_noise_fractions + 1 - indexes) / 2
        return high_noise_intervals, fractions, self.get_fraction(high_noise_intervals)

    def get_intelligibility(self):
        """
        Analyses intelligibility of speech
        @return: approximate intelligibility per file fragment and summary intelligibility
        """
        # collect basic intelligibility measures
        intelligibility = Intelligibility(self.path, self.all_words_without_noise, self.noise,
                                          self.analyzed_segment_len)
        indexes, fast_intervals, noisy_intervals = intelligibility.get_intelligibility_features()
        # transform to fractions on whole file
        fast_fraction = self.get_fraction(fast_intervals)
        noisy_fraction = self.get_fraction(noisy_intervals)
        index_fraction = np.average(indexes)
        logger.debug("Fast fraction: " + str(fast_fraction))
        logger.debug("Noisy fraction: " + str(noisy_fraction))
        logger.debug("Index fraction: " + str(index_fraction))
        # transform to fractions per file fragment
        noisy_fractions = np.array(self.get_fractions_from_intervals(noisy_intervals))
        fast_fractions = np.array(self.get_fractions_from_intervals(fast_intervals))

        # count average
        negative_fractions = (noisy_fractions + fast_fractions + (1 - indexes)) / 3
        negative_fraction = (fast_fraction + noisy_fraction + (1 - index_fraction)) / 3
        return negative_fractions, negative_fraction

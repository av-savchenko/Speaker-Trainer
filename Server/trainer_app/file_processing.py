from datetime import time
from django.forms import model_to_dict
from .recommendations import *
from .forms import *
from .models import *
from .computer_vision.draw import *
from .computer_vision.subsystem import *
from .speech_processing.speech_processing_subsystem import *


class FileProcessingSystem:
    """
    Class for file analysis
    """
    def __init__(self, file: FileInfo, analyzed_segment_len, language_flag="Russian"):
        """
        Initializing of file and its params
        @param file: FileInfo instance to analyze
        @param analyzed_segment_len: length of one file fragment to analyze
        @param language_flag: text language flag (for recommendations and statistics)
        """
        self.file = file
        self.file_path = file.file.path
        self.file_id = file.id
        self.analyzed_segment_len = analyzed_segment_len
        self.language_flag = language_flag
        negative_emotions = []
        negative_emotions_bool = []
        for emotion in Emotions.objects.all():
            if emotion not in file.preferred_emotions.all():
                negative_emotions.append(emotion.name)
                negative_emotions_bool.append(True)
            else:
                negative_emotions_bool.append(False)

        logger.debug("not preferred emotions: " + str(negative_emotions))
        self.negative_emotions_bool = negative_emotions_bool
        self.computer_vision = VideoSubsystem(self.file_path, negative_emotions, emotions=file.emotionality_flag,
                                              gesticulation=file.gestures_flag, angle=file.angle_flag,
                                              gaze=file.glances_flag, clothes=file.clothes_flag)
        self.computer_vision.process_video(duration=analyzed_segment_len)
        self.speech_processing = SpeechProcessingSubsystem(self.file_path, negative_emotions_bool,
                                                           analyzed_segment_len=analyzed_segment_len)

    def save_timestamps_to_db(self, timestamps, type_choice):
        """
        Saves timestamps of low speech rate or high background noise to database
        @param timestamps: periods to be saved
        @param type_choice: 0 for background noise, 1 for speech rate
        """
        for time_period in timestamps:
            start_seconds, end_seconds = round(time_period[0]), round(time_period[1])
            # transform seconds to time type
            start = time(hour=start_seconds // 3600, minute=start_seconds // 60, second=start_seconds % 60)
            end = time(hour=end_seconds // 3600, minute=end_seconds // 60, second=end_seconds % 60)
            form = FileTimestampsForm(
                {"file_id": self.file_id, "start": start, "end": end, "time_period_type": type_choice})
            if form.is_valid():
                form.save()
            else:
                logger.debug("Saving timestamps to database errors: " + str(form.errors))

    def save_fractions_to_db(self, fractions, type_choice):
        """
        Saves fractions (analysis results) per file fragment to database
        @param fractions: list of fractions (percentages)
        @param type_choice: type of analysis parameter (see models.FilePeriodicGrades)
        """
        for idx, fraction in enumerate(fractions):
            form = FilePeriodicGradesForm(
                {"file_id": self.file_id, "period_num": idx, "time_period_type": type_choice, "value": fraction}
            )
            if form.is_valid():
                form.save()
            else:
                logger.debug("Saving fractions to database errors: " + str(form.errors))

    def get_transcription(self):
        """
        Translates and saves file transcription
        """
        self.speech_processing.speech_recognition()
        # self.file.text = self.speech_processing.transcription["text"].strip()
        self.file.text = self.speech_processing.cleaned_transcription
        self.file.save()

    def get_emotionality(self):
        """
        Gets emotionality from audio and video subsystems, unites them and saves neutral emotion fraction
        """
        video_emotions = self.computer_vision.get_inappropriate_emotion_percentage()
        video_neutral_emotions = self.computer_vision.get_emotions()

        try:
            audio_emotions, audio_neutral_emotions = self.speech_processing.get_emotionality()
        except Exception as e:
            logger.debug("Audio emotions error: " + str(e.args))
            audio_emotions = self.computer_vision.get_inappropriate_emotion_percentage()
            audio_neutral_emotions = self.computer_vision.get_emotions()
        audio_emotions = np.array(audio_emotions)
        video_emotions = np.array(video_emotions)
        incorrect_emotions_percentage = (2 * video_emotions + audio_emotions) / 3
        incorrect_emotions_percentage = np.round(np.array(incorrect_emotions_percentage), 3)
        emotions_fraction = round(np.sum(incorrect_emotions_percentage) / len(incorrect_emotions_percentage), 3)
        logger.debug("negative emotions fraction: " + str(emotions_fraction))
        self.save_fractions_to_db(incorrect_emotions_percentage, 2)
        self.file.emotionality = round(emotions_fraction, 3)

        neutral_emotions = (np.array(video_neutral_emotions) + np.array(audio_neutral_emotions)) / 2
        neutral_emotions_fraction = round(np.sum(neutral_emotions) / len(neutral_emotions), 3)
        self.file.neutral_emotionality = round(neutral_emotions_fraction, 3)
        self.file.save()

    def get_filler_words(self):
        """
        Gets filler words and phrases, saves them and their count per minute
        """
        all_filler_words, worst_filler_words = self.speech_processing.get_filler_words()
        for word in all_filler_words:
            data = {"file_id": self.file_id, "word_or_phrase": word, "occurrence": all_filler_words[word]}
            if word in worst_filler_words:
                data["most_common"] = True
            form = FillerWordsForm(data=data)
            if form.is_valid():
                form.save()
            else:
                logger.debug("Saving filler-words to database errors: " + str(form.errors))
        overall_count = sum(list(all_filler_words.values()))
        words_per_minute_percentage = round((overall_count / (self.speech_processing.duration / 60)) / 10, 5)
        self.file.clean_speech = max(0, 1 - words_per_minute_percentage)
        self.file.save()

    def get_speech_rate(self):
        """
        Gets and saves intervals with slow speech rate and their percentage
        """
        intervals, fractions, final_fraction = self.speech_processing.get_speech_rate()
        self.save_timestamps_to_db(intervals, 1)
        self.save_fractions_to_db(fractions, 1)
        self.file.speech_rate = final_fraction
        self.file.save()

    def get_background_noise(self):
        """
        Gets and saves intervals with high background noise and their percentage
        """
        intervals, fractions, final_fraction = self.speech_processing.get_background_noise()
        fractions = np.round(fractions, 3)
        self.save_timestamps_to_db(intervals, 0)
        self.save_fractions_to_db(fractions, 0)
        self.file.background_noise = final_fraction
        self.file.save()

    def get_intelligibility(self):
        """
        Gets and saves intelligibility estimation
        """
        negative_fractions, negative_index = self.speech_processing.get_intelligibility()
        logger.debug("negative_index: " + str(negative_index))
        fractions = np.round(1 - negative_fractions, 3)
        self.save_fractions_to_db(fractions, 3)
        self.file.intelligibility = max(0, (1 - negative_index))
        self.file.save()

    def get_incorrect_angle(self):
        """
        Gets and saves incorrect angle percentage
        """
        incorrect_angle_fractions = self.computer_vision.get_angle()
        incorrect_angle_fractions = np.round(np.array(incorrect_angle_fractions), 3)
        self.save_fractions_to_db(incorrect_angle_fractions, 6)

        incorrect_angle = round(np.sum(incorrect_angle_fractions) / len(incorrect_angle_fractions), 3)
        self.file.angle = incorrect_angle
        self.file.save()

    def get_incorrect_glances(self):
        """
        Gets and saves incorrect glances percentage
        """
        incorrect_glance_fractions = self.computer_vision.get_gaze()
        incorrect_glance_fractions = np.round(np.array(incorrect_glance_fractions), 3)
        self.save_fractions_to_db(incorrect_glance_fractions, 5)
        incorrect_glance = round(np.sum(incorrect_glance_fractions) / len(incorrect_glance_fractions), 3)
        self.file.glances = incorrect_glance
        self.file.save()

    def get_gestures(self):
        """
        Gets and saves gesticulation level
        """
        gestures = self.computer_vision.get_gestures()
        gestures = np.round(np.array(gestures), 3)
        self.save_fractions_to_db(gestures, 4)
        final_gesture_fraction = round(np.sum(gestures) / len(gestures), 3)
        self.file.gestures = final_gesture_fraction
        self.file.save()

    def get_clothes(self):
        """
        Gets and saves clothes suitability
        """
        clothes = self.computer_vision.get_clothes_estimation()
        self.file.clothes = int(clothes)
        self.file.save()

    def draw(self):
        """
        Draw analysis result signatures on video file
        """
        # indexes of best values for each parameter
        optimal_indexes = {
            "background_noise": 0,
            "speech_rate": 0,
            "emotionality": 0,
            "intelligibility": 2,
            "gestures": [gesture.id - 1 for gesture in self.file.preferred_gestures.all()],
            "glances": 0,
            "lightning": 0,
        }
        file_dict = model_to_dict(self.file)
        lst = ORDER[:-1]
        # texts to put into file
        text_values = []
        # boolean values (True - optimal) for text color
        boolean_flags = []
        for period_index, name in enumerate(lst):
            if file_dict[name + "_flag"]:
                text_values.append([])
                boolean_flags.append([])
                # get grades for parameter for each file fragment
                res = FilePeriodicGrades.objects.filter(
                    file_id=self.file_id,
                    time_period_type=period_index).\
                    order_by("period_num")
                # transform grade into text
                for grade in res:
                    value = grade.value
                    text_idx = 0
                    if value > CONSTANTS[name][1]:
                        text_idx = 2
                    elif value > CONSTANTS[name][0]:
                        text_idx = 1
                    text = LANGUAGE[self.language_flag]["DRAW_VALUES"][name][text_idx]
                    text_values[-1].append(text)
                    # append text color
                    if name == "gestures":
                        boolean_flags[-1].append(text_idx in optimal_indexes[name])
                    else:
                        boolean_flags[-1].append(text_idx == optimal_indexes[name])

        # append values on lightning if possible
        lightning_numbers = self.computer_vision.get_lightning()
        if len(lightning_numbers) > 0:
            text_values.append([])
            boolean_flags.append([])
            for val in lightning_numbers:
                text_values[-1].append(LANGUAGE[self.language_flag]["DRAW_VALUES"]["lightning"][val])
                boolean_flags[-1].append(val == 1)

        draw_res = DrawResults(self.file_path, dist=self.analyzed_segment_len)
        # path for temporary file
        painted_path = self.file_path[:self.file_path.rfind('.')] + '_painted.' + \
                       self.file_path[self.file_path.rfind('.')+1:]
        # file is saved without noise
        draw_res.draw(painted_path, text_values, boolean_flags,
                      self.computer_vision.get_angle_len(), self.computer_vision.get_incorrect_angle_ind())

        final_path = self.file_path
        # unite video and audio
        output = mp_editor.VideoFileClip(painted_path)
        final_duration = output.duration
        output_audio = mp_editor.VideoFileClip(self.file_path).audio.subclip(0, final_duration)
        output.audio = output_audio
        output.write_videofile(final_path)
        # remove temporary file
        if os.path.isfile(painted_path):
            os.remove(painted_path)

from django.db import models
from django.core.validators import MinLengthValidator


class Authentication(models.Model):
    """
    Class with user info - email, password, unique id, generated token, id of file with best fragment
    """
    id = models.IntegerField(primary_key=True, db_index=True)
    email = models.EmailField(max_length=100, unique=True, db_index=True)
    password = models.CharField(max_length=100, validators=[MinLengthValidator(6)])
    token = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    register_date = models.DateField(null=True, blank=True, db_index=True)

    best_file_num = models.IntegerField(blank=True, default=-1)

    def __str__(self):
        return self.email


class Emotions(models.Model):
    """
    Class with fixed set of emotions (see fixtures/emotions.json)
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)


class Gestures(models.Model):
    """
    Class with fixed set of gestures (see fixtures/gestures.json)
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)


class FileInfo(models.Model):
    """
    Class with all file info - path, user's id, time of receipt, chosen analysis parameters, analysis results
    """
    id = models.IntegerField(primary_key=True, db_index=True)
    user_id = models.ForeignKey("Authentication", to_field="id", on_delete=models.CASCADE, db_index=True)
    file = models.FileField(upload_to="uploads/")
    filename = models.CharField(max_length=100)
    register_date = models.DateTimeField(db_index=True)

    emotionality_flag = models.BooleanField(default=False)
    neutral_emotionality_flag = models.BooleanField(default=False)

    clean_speech_flag = models.BooleanField(default=False)
    speech_rate_flag = models.BooleanField(default=False)
    background_noise_flag = models.BooleanField(default=False)
    intelligibility_flag = models.BooleanField(default=False)

    gestures_flag = models.BooleanField(default=False)
    clothes_flag = models.BooleanField(default=False)
    angle_flag = models.BooleanField(default=False)
    glances_flag = models.BooleanField(default=False)

    analyzed_segment_len = models.IntegerField()
    file_type = models.BooleanField(default=False)

    preferred_emotions = models.ManyToManyField(Emotions, null=True, blank=True)
    preferred_gestures = models.ManyToManyField(Gestures, null=True, blank=True)

    UNKNOWN = -1
    LOW = 0
    NORMAL = 1
    HIGH = 2
    STATUS_CHOICES = (
        (UNKNOWN, "UNKNOWN"),
        (LOW, "Low"),
        (NORMAL, "Normal"),
        (HIGH, "High"),
    )

    clean_speech = models.DecimalField(max_digits=15, decimal_places=10, blank=True, default=-1)
    speech_rate = models.DecimalField(max_digits=12, decimal_places=10, blank=True, default=-1)
    background_noise = models.DecimalField(max_digits=12, decimal_places=10, blank=True, default=-1)
    intelligibility = models.DecimalField(max_digits=12, decimal_places=10, blank=True, default=-1)

    clothes = models.IntegerField(choices=STATUS_CHOICES, blank=True, default=UNKNOWN)
    gestures = models.IntegerField(choices=STATUS_CHOICES, blank=True, default=UNKNOWN)
    angle = models.DecimalField(max_digits=12, decimal_places=10, blank=True, default=-1)
    glances = models.DecimalField(max_digits=12, decimal_places=10, blank=True, default=-1)

    emotionality = models.DecimalField(max_digits=12, decimal_places=10, blank=True, default=-1)
    neutral_emotionality = models.DecimalField(max_digits=12, decimal_places=10, blank=True, default=-1)
    text = models.TextField(null=True, blank=True)

    best_segment_num = models.IntegerField(blank=True, default=-1)
    best_segment_value = models.DecimalField(max_digits=12, decimal_places=10, blank=True, default=-1)


class FileTimestamps(models.Model):
    """
    Class of timestamps for background noise or pause intervals
    """
    NOISE = 0
    PAUSE = 1
    TYPE_CHOICES = (
        (NOISE, "NOISE"),
        (PAUSE, "PAUSE"),
    )
    file_id = models.ForeignKey("FileInfo", to_field="id", on_delete=models.CASCADE, db_index=True)
    start = models.TimeField()
    end = models.TimeField()
    time_period_type = models.IntegerField(choices=TYPE_CHOICES)


class FillerWords(models.Model):
    """
    Class for filler words / phrases - their occurrence and whether they are common for a file
    """
    file_id = models.ForeignKey("FileInfo", to_field="id", on_delete=models.CASCADE, db_index=True)
    word_or_phrase = models.CharField(max_length=100)
    occurrence = models.IntegerField(default=0)
    most_common = models.BooleanField(default=False)


class FilePeriodicGrades(models.Model):
    """
    Class of analysis result values for all base parameters for each file fragment
    """
    NOISE = 0
    PAUSES = 1
    EMOTIONS = 2
    INTELLIGIBILITY = 3
    GESTURES = 4
    GLANCES = 5
    ANGLE = 6
    TYPE_CHOICES = (
        (NOISE, "NOISE"),
        (PAUSES, "PAUSE"),
        (EMOTIONS, "EMOTIONS"),
        (INTELLIGIBILITY, "INTELLIGIBILITY"),
        (GESTURES, "GESTURES"),
        (GLANCES, "GLANCES"),
        (ANGLE, "ANGLE")
    )
    file_id = models.ForeignKey("FileInfo", to_field="id", on_delete=models.CASCADE, db_index=True)
    period_num = models.IntegerField()
    time_period_type = models.IntegerField(choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=8, decimal_places=6)

from django import forms
from .models import *


class AuthenticationForm(forms.ModelForm):
    class Meta:
        model = Authentication
        fields = "__all__"


class FileInfoForm(forms.ModelForm):
    class Meta:
        model = FileInfo
        fields = "__all__"


class FileTimestampsForm(forms.ModelForm):
    class Meta:
        model = FileTimestamps
        fields = "__all__"


class FillerWordsForm(forms.ModelForm):
    class Meta:
        model = FillerWords
        fields = "__all__"


class FilePeriodicGradesForm(forms.ModelForm):
    class Meta:
        model = FilePeriodicGrades
        fields = "__all__"


class EmotionsForm(forms.ModelForm):
    class Meta:
        model = Emotions
        fields = "__all__"


class GesturesForm(forms.ModelForm):
    class Meta:
        model = Gestures
        fields = "__all__"

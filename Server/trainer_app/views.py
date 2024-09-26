import csv
import hashlib
import secrets
import datetime
import json
import ffmpeg
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path
from django.core.files import File
from django.db.models import Max
from django.http import HttpResponse, FileResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from statistics import mean
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import user_passes_test
from .file_processing import *
from .forms import *
from .models import *
from .recommendations import *

# values for graphics on the main screen

demo_values = ["emotionality", "neutral_emotionality"]
# message for client part
operation_completed_successfully = "ok"
# all messages language
language_flag = "Russian"
# whether to send lists of timestamps
append_timestamps = False


@csrf_exempt
def register_email_confirm(request):
    """
    Email confirming for registration (sending message with code to specified email)
    Checks if email is valid and not already registered
    @param request: request with user's email
    @return: four-number code for email confirmation if email is valid and not already registered in system,
    error message otherwise
    """
    # creating test user to confirm email
    query_dict = request.POST.copy()
    if Authentication.objects.count() == 0:
        person_id = 1
    else:
        person_id = Authentication.objects.aggregate(Max('id'))['id__max'] + 1
    query_dict.appendlist("id", person_id)
    register_date = datetime.date.today()
    query_dict.appendlist("register_date", register_date)
    query_dict.appendlist("password", "test_password")
    form = AuthenticationForm(query_dict)
    if form.is_valid():
        logger.debug("Registration: valid email, message is sent.")
        email = request.POST.get("email")
        # generating four-number code and sending it to email and to client part
        code = secrets.choice(seq=range(1000, 10000))
        send_message(email, code)
        return HttpResponse(code, headers={"status": operation_completed_successfully})
    else:
        logger.debug("Registration (email confirm) errors: " + str(form.errors.as_data()))
        if "email" in form.errors.as_data():
            text_error = str(form.errors["email"][0])
            return HttpResponse("email_error", headers={"status": text_error})
        return HttpResponseServerError("unknown_error",
                                       headers={"status": "Application error. Please contact support."})


@csrf_exempt
def register_save(request):
    """
    Registers user, checks if password is valid
    @param request: request with email and password
    @return: token if registration is successful, error message otherwise
    """
    # creating user with id one unit greater than max id in system
    query_dict = request.POST.copy()
    if Authentication.objects.count() == 0:
        person_id = 1
    else:
        person_id = Authentication.objects.aggregate(Max('id'))['id__max'] + 1
    query_dict.appendlist("id", person_id)
    register_date = datetime.date.today()
    query_dict.appendlist("register_date", register_date)
    form = AuthenticationForm(query_dict)
    if form.is_valid():
        logger.debug("Registration: valid info, user is registered.")
        user = form.save(commit=False)
        # generating auth token for further identification
        token = secrets.token_hex(16)
        user.token = token
        # hashing password
        hash_object = hashlib.sha256(user.password.encode())
        hex_dig = hash_object.hexdigest()
        user.password = hex_dig
        user.save()
        return HttpResponse(token, headers={"status": operation_completed_successfully})
    else:
        logger.debug("Registration (user saving) errors: " + str(form.errors.as_data()))
        if "password" in form.errors.as_data():
            text_error = str(form.errors["password"][0])
            return HttpResponse("password_error", headers={"status": text_error})
        return HttpResponseServerError("unknown_error",
                                       headers={"status": "Application error. Please contact support."})


@csrf_exempt
def login(request):
    """
    Logins user, checks email and password
    @param request: request with email and password
    @return: token if registration is successful, error message otherwise
    """
    email = request.POST.get("email")
    user = Authentication.objects.filter(email=email)
    if not user.exists():
        return HttpResponse("email_error", headers={"status": "Email is not registered."})
    user = user[0]
    hash_object = hashlib.sha256(request.POST.get("password").encode())
    hex_dig = hash_object.hexdigest()
    if user.password != hex_dig:
        return HttpResponse("password_error", headers={"status": "Incorrect password."})
    token = secrets.token_hex(16)
    user.token = token
    user.save()
    return HttpResponse(token, headers={"status": operation_completed_successfully})


@csrf_exempt
def logout(request):
    """
    Logouts user (deletes token)
    @param request: request with user's token
    @return: success message if logout is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    user = user[0]
    user.token = None
    user.save()
    return HttpResponse(operation_completed_successfully, headers={"status": operation_completed_successfully})


@csrf_exempt
def password_recovery_email_confirm(request):
    """
    Request for password recovery
    @param request: request with user's email
    @return: four-number code for email confirmation if email is registered, error message otherwise
    """
    email = request.POST.get("email")
    user = Authentication.objects.filter(email=email)
    if not user.exists():
        return HttpResponse("email_error", headers={"status": "Email is not registered."})
    code = secrets.choice(seq=range(1000, 10000))
    send_message(email, code)
    return HttpResponse(code, headers={"status": operation_completed_successfully})


@csrf_exempt
def password_recovery_save(request):
    """
    Updates password
    @param request: request with user's email and new password
    @return: token if password update is successful, error message otherwise
    """
    email = request.POST.get("email")
    user = Authentication.objects.filter(email=email)
    if not user.exists():
        return HttpResponseServerError("email_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    user = user[0]
    password = request.POST.get("password")
    if len(password) < 6:
        status = f"Ensure this value has at least 6 characters (it has {len(password)})."
        return HttpResponse("password_error", headers={"status": status})
    if len(password) > 100:
        status = f"Ensure this value has at most 100 characters (it has {len(password)})."
        return HttpResponse("password_error", headers={"status": status})
    # password hashing
    hash_object = hashlib.sha256(password.encode())
    hex_dig = hash_object.hexdigest()
    user.password = hex_dig
    # token generating
    token = secrets.token_hex(16)
    user.token = token
    user.save()
    return HttpResponse(token, headers={"status": operation_completed_successfully})


@csrf_exempt
def upload_file(request):
    """
    Uploads user's file and analyses it
    @param request: request with user's token, file and chosen analysis parameters
    @return: file id if analysis is successful, error message otherwise
    """
    logger.debug("file uploading params: " + str(request.POST))
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    user = user[0]
    user_id = user.id
    query_dict = request.POST.copy()
    query_dict.appendlist("neutral_emotionality", request.POST.get("emotionality"))
    # changing names for binary data (parameters flags)
    for key in fields:
        value = query_dict[key]
        query_dict.pop(key)
        query_dict.appendlist(key + "_flag", value)
    query_dict.appendlist("register_date", datetime.datetime.now())
    query_dict.appendlist("user_id", user_id)
    if FileInfo.objects.count() == 0:
        file_id = 1
    else:
        file_id = FileInfo.objects.aggregate(Max('id'))['id__max'] + 1
    query_dict.appendlist("id", file_id)
    query_dict.pop("token")
    query_dict.pop("undesirable_emotions")
    query_dict.pop("undesirable_gestures")
    logger.debug("Query dict: " + str(query_dict))
    form = FileInfoForm(query_dict, request.FILES)
    if form.is_valid():
        form.save()
        file_info = FileInfo.objects.get(id=file_id)
        path = file_info.file.path
        # transforming file to mp4 format if necessary
        if path[-3:] != "mp4":
            logger.debug("To mp4")
            name, ext = os.path.splitext(path)
            out_name = name + ".mp4"
            ffmpeg.input(path).output(out_name).run()
            out_name_path = Path(out_name)
            with out_name_path.open(mode="rb") as f:
                file_info.file = File(f, name=out_name_path.name)
                file_info.save()
            os.remove(out_name)
            os.remove(path)

        undesirable_emotions_list = json.loads(request.POST.get("undesirable_emotions"))
        logger.debug("undesirable_emotions_list: " + str(undesirable_emotions_list))
        # attach desirable emotions from corresponding table
        for i, undesirable_emotion in enumerate(undesirable_emotions_list):
            if not undesirable_emotion:
                emotion = Emotions.objects.get(id=i + 1)
                file_info.preferred_emotions.add(emotion)

        # attach desirable gestures from corresponding table
        undesirable_gestures_list = json.loads(request.POST.get("undesirable_gestures"))
        logger.debug("undesirable_gestures_list: " + str(undesirable_gestures_list))
        for i, undesirable_gesture in enumerate(undesirable_gestures_list):
            if not undesirable_gesture:
                gesture = Gestures.objects.get(id=i + 1)
                file_info.preferred_gestures.add(gesture)

        file_info.save()
        # get file image (for further usage in archive)
        get_screenshot(file_info)
        analyzed_segment_len = int(request.POST.get("analyzed_segment_len"))
        if not file_processing(file_info, user, analyzed_segment_len=analyzed_segment_len):
            return HttpResponseServerError("analysis_error", headers={"status": "Application error. Please contact "
                                                                                "support."})
        return HttpResponse(str(file_id), headers={"status": operation_completed_successfully})
    elif "filename" in form.errors.as_data():
        return HttpResponse("filename_error", headers={"status": str(form.errors["filename"][0])})
    else:
        logger.debug("File uploading errors: " + str(form.errors.as_data()))
        return HttpResponseServerError("parsing_error",
                                       headers={"status": "Application error. Please contact support."})


@csrf_exempt
def archive_number_of_files(request):
    """
    Sends number of user's files and their ids
    @param request: request with user's token
    @return: files' count and list of their ids in JSON format if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error", headers={"status": "Application error. Please contact "
                                                                                   "support."})
    user_id = user[0].id
    files = FileInfo.objects.filter(user_id=user_id)
    file_ids = [file.id for file in files]
    files_info = {"num_of_files": files.count(), "file_ids": file_ids}
    logger.debug("files info: " + str(files_info))
    return HttpResponse(json.dumps(files_info), headers={"status": operation_completed_successfully})


@csrf_exempt
def archive_file_info(request):
    """
    Sends base file info
    @param request: request with user's token and file id
    @return: file's name and date of receiving in JSON format if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error", headers={"status": "Application error. Please contact "
                                                                                   "support."})
    file = FileInfo.objects.filter(id=request.POST.get("file_id"))
    if not file.exists():
        return HttpResponseServerError("file_not_found_error", headers={"status": "Application error. Please contact "
                                                                                  "support."})
    file = file[0]
    if user[0].id != file.user_id.id:
        return HttpResponseServerError("file_and_token_do_not_match_error",
                                       headers={"status": "Application error. Please contact support."})
    file_info = {"filename": file.filename, "datetime": file.register_date.strftime("%Y:%m:%d %H:%M:%S")}
    logger.debug("file info: " + str(file_info))
    return HttpResponse(json.dumps(file_info), headers={"status": operation_completed_successfully})


@csrf_exempt
def archive_file_image(request):
    """
    Sends file image (in png format) for archive preview
    @param request: request with user's token and file id
    @return: image file (screenshot from video) if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file = FileInfo.objects.filter(id=request.POST.get("file_id"))
    if not file.exists():
        return HttpResponseServerError("file_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file = file[0]
    if user[0].id != file.user_id.id:
        return HttpResponseServerError("file_and_token_do_not_match_error",
                                       headers={"status": "Application error. Please contact support."})
    path = file.file.path
    image_path = path[:path.rfind('.')] + '.png'
    return FileResponse(open(image_path, "rb"), headers={"status": operation_completed_successfully})


@csrf_exempt
def video_file(request):
    """
    Sends modified video file (with signatures)
    @param request: request with user's token and file id
    @return: video file if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    file_id = request.POST.get("file_id")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file = FileInfo.objects.filter(id=file_id)
    if not file.exists():
        return HttpResponseServerError("file_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    if user[0].id != file[0].user_id.id:
        return HttpResponseServerError("file_and_token_do_not_match_error",
                                       headers={"status": "Application error. Please contact support."})
    path = file[0].file.path
    return FileResponse(open(path, "rb"), headers={"status": operation_completed_successfully})


@csrf_exempt
def delete_file(request):
    """
    Deletes video file
    @param request: request with user's token and file id
    @return: success message if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    file_id = request.POST.get("file_id")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file = FileInfo.objects.filter(id=file_id)
    if not file.exists():
        return HttpResponseServerError("file_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    user = user[0]
    if user.id != file[0].user_id.id:
        return HttpResponseServerError("file_and_token_do_not_match_error",
                                       headers={"status": "Application error. Please contact support."})
    file = file[0]
    file_id = file.id
    path = file.file.path
    file.delete()
    # delete additional files
    paths = [path, path[:path.rfind('.')] + '.png', path[:path.rfind('.')] + '.wav']
    for path in paths:
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.debug("Error while deleting: " + path + " " + str(e.args))

    # rewrite best user's file if deleted file was the best
    if user.best_file_num == file_id:
        logger.debug("Change best file on delete")
        files = FileInfo.objects.filter(user_id=user.id)
        # num = -1 if user doesn't have any other files
        if files.count() == 0:
            user.best_file_num = -1
        else:
            best_value = -1
            best_file = -1
            for file in files:
                value = file.best_segment_value
                if value != -1 and (value < best_value or best_value == -1):
                    best_value = value
                    best_file = file.id
            user.best_file_num = best_file
        user.save()
    return HttpResponse("ok", headers={"status": operation_completed_successfully})


@csrf_exempt
def file_statistics(request):
    """
    Sends file analysis results
    @param request: request with user's token and file id
    @return: file statistics converted to text format, timestamps and filler words in JSON format
    if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    file_id = request.POST.get("file_id")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file_info = FileInfo.objects.filter(id=file_id)
    if not file_info.exists():
        return HttpResponseServerError("file_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    if user[0].id != file_info[0].user_id.id:
        return HttpResponseServerError("file_and_token_do_not_match_error",
                                       headers={"status": "Application error. Please contact support."})
    file = file_info[0]
    # Transform real numbers to text grades according to limit values
    data = model_to_dict(file, fields=fields)
    data = convert_to_text(data, file.file_type)

    # Save timestamps lists in string format
    background_noise_timestamps, low_speech_rate_timestamps = [], []
    timestamps = FileTimestamps.objects.filter(file_id=file_id)
    for timestamp in timestamps:
        start = timestamp.start.strftime("%H:%M:%S")
        end = timestamp.end.strftime("%H:%M:%S")
        if timestamp.time_period_type == 0:
            background_noise_timestamps.append([start, end])
        else:
            low_speech_rate_timestamps.append([start, end])
    if append_timestamps:
        data["background_noise_timestamps"] = background_noise_timestamps
        data["low_speech_rate_timestamps"] = low_speech_rate_timestamps
    data["analyzed_segment_len"] = file.analyzed_segment_len
    # adding most common filler words
    filler_words_lst = FillerWords.objects.filter(file_id=file_id, most_common=True)
    filler_words = [word.word_or_phrase for word in filler_words_lst]
    data["filler_words"] = filler_words
    # adding real values (analysis results) for graphics
    data = data | collect_lists(file)
    logger.debug("statistics data: " + str(data))
    res = json.dumps(data, default=float)
    return HttpResponse(res, headers={"status": operation_completed_successfully})


@csrf_exempt
def statistics(request):
    """
    Sends user statistics (real values for each file, filler words count)
    @param request: request with user's token
    @return: user statistics as lists of values, filler words and their percentage in JSON format
    if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})

    all_data, ids_lst = get_user_stats(user[0].id)
    data = dict()
    for value in demo_values:
        data[value] = all_data[value]
    filler_words_objects = FillerWords.objects.filter(file_id__in=ids_lst)
    filler_words_dict = dict()
    for filler_word_object in filler_words_objects:
        word = filler_word_object.word_or_phrase
        if word in FillerWordsAndPhrases.params["parasites"] or \
                word in FillerWordsAndPhrases.params["parasite_phrases"]:
            if word not in filler_words_dict:
                filler_words_dict[word] = 0
            filler_words_dict[word] += filler_word_object.occurrence
    total_count = sum(list(filler_words_dict.values()))
    filler_words_list = sorted(list(filler_words_dict.items()), key=lambda x: -x[1])
    # most common filler words (if more then five - fifth and subsequent are united into 'other' group)
    if len(filler_words_list) > 5:
        filler_words_list = filler_words_list[:4]
        other_count = total_count - sum([filler_word[1] for filler_word in filler_words_list])
        filler_words_list.append(("Прочее", other_count))
    data["filler_words"] = [filler_word[0] for filler_word in filler_words_list]
    data["filler_words_percentage"] = [filler_word[1] / total_count for filler_word in filler_words_list]
    logger.debug("statistics: " + str(data))
    res = json.dumps(data, default=float)
    return HttpResponse(res, headers={"status": operation_completed_successfully})


@csrf_exempt
def user_recommendations_description(request):
    """
    Sends recommendations for each parameter based on averaged files statistics
    @param request: request with user's token
    @return: text recommendations in JSON format if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    data, _ = get_user_stats(user[0].id)
    for key in data:
        if len(data[key]) == 0:
            data[key].append(-1)
        constants_key = key
        if key == "neutral_emotionality":
            constants_key = "neutral_emotionality_official"
        new_val = mean(data[key])
        # transcription into recommendations indexes
        if new_val > CONSTANTS[constants_key][1]:
            new_val = 2
        elif new_val > CONSTANTS[constants_key][0]:
            new_val = 1
        elif new_val > -1:
            new_val = 0
        # transcription into texts
        data[key] = LANGUAGE[language_flag]["RECOMMENDATIONS_TEXTS"][key][new_val]

    # unite recommendations on incorrect emotions and on neutral emotion fraction
    if "emotionality" in data:
        data["emotionality"] += " " + data["neutral_emotionality"]
        del data["neutral_emotionality"]
    logger.debug("User recommendations: " + str(data))
    res = json.dumps(data, default=float)
    return HttpResponse(res, headers={"status": operation_completed_successfully})


@csrf_exempt
def user_recommendations_sample(request):
    """
    Sends best file fragment among all user's files (its length is equal to analysis segment length parameter)
    @param request: request with user's token
    @return: file fragment is request is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})

    user = user[0]
    file_id = user.best_file_num
    if file_id == -1:
        return HttpResponse("no_files_uploaded", headers={"status": "User has not uploaded any files."})
    best_file = FileInfo.objects.get(id=file_id)
    segment_num = best_file.best_segment_num
    length = best_file.analyzed_segment_len

    # paths for N-second sub clip
    path = os.path.abspath(os.path.dirname(__file__))
    subclip_path = os.path.abspath(os.path.join(path, "file_processing/fragment.mp4"))

    path = best_file.file.path
    clip = mp_editor.VideoFileClip(path)
    subclip = clip.subclip(segment_num * length, segment_num * length + length)
    subclip.write_videofile(subclip_path, logger=None)
    return FileResponse(open(subclip_path, "rb"), headers={"status": operation_completed_successfully})


@csrf_exempt
def file_recommendations_description(request):
    """
    Sends recommendations for each parameter based on file statistics
    @param request: request with user's token and file id
    @return: text recommendations in JSON format if request is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file = FileInfo.objects.filter(id=request.POST.get("file_id"))
    if not file.exists():
        return HttpResponseServerError("file_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file = file[0]
    if user[0].id != file.user_id.id:
        return HttpResponseServerError("file_and_token_do_not_match_error",
                                       headers={"status": "Application error. Please contact support."})

    data = {}
    analysis = model_to_dict(file)
    for key in fields:
        new_val = analysis[key]
        constants_key = key
        if key == "neutral_emotionality":
            if file.file_type:
                constants_key = "neutral_emotionality_official"
            else:
                constants_key = "neutral_emotionality_nonofficial"
        # transcript into recommendations indexes
        if new_val > CONSTANTS[constants_key][1]:
            new_val = 2
        elif new_val > CONSTANTS[constants_key][0]:
            new_val = 1
        elif new_val > -1:
            new_val = 0
        # transcription into texts
        if key == "gestures" and new_val > -1:
            preferred_gestures = [gesture.id - 1 for gesture in file.preferred_gestures.all()]
            data[key] = LANGUAGE[language_flag]["RECOMMENDATIONS_TEXTS"]["gestures_dynamic"][new_val][0]
            if new_val in preferred_gestures:
                data[key] += LANGUAGE[language_flag]["RECOMMENDATIONS_TEXTS"]["gestures_dynamic"][new_val][1]
            else:
                for preferred_gesture_id in preferred_gestures:
                    data[key] += \
                        LANGUAGE[language_flag]["RECOMMENDATIONS_TEXTS"]["gestures_dynamic"][preferred_gesture_id][2]
        else:
            data[key] = LANGUAGE[language_flag]["RECOMMENDATIONS_TEXTS"][key][new_val]
    # unite recommendations on incorrect emotions and on neutral emotion fraction
    if "emotionality" in data:
        data["emotionality"] += " " + data["neutral_emotionality"]
        del data["neutral_emotionality"]
    logger.debug("File recommendations: " + str(data))
    res = json.dumps(data, default=float)
    return HttpResponse(res, headers={"status": operation_completed_successfully})


@csrf_exempt
def file_recommendations_sample(request):
    """
    Sends best file fragment (its length is equal to analysis segment length parameter)
    @param request: request with user's token and file id
    @return: file fragment is request is successful, error message otherwise
    """
    token = request.POST.get("token")
    user = Authentication.objects.filter(token=token)
    if not user.exists():
        return HttpResponseServerError("token_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file = FileInfo.objects.filter(id=request.POST.get("file_id"))
    if not file.exists():
        return HttpResponseServerError("file_not_found_error",
                                       headers={"status": "Application error. Please contact support."})
    file = file[0]
    if user[0].id != file.user_id.id:
        return HttpResponseServerError("file_and_token_do_not_match_error",
                                       headers={"status": "Application error. Please contact support."})
    segment_num = file.best_segment_num
    length = file.analyzed_segment_len

    # path for N-second sub clips
    path = os.path.abspath(os.path.dirname(__file__))
    subclip_path = os.path.abspath(os.path.join(path, "file_processing/fragment.mp4"))
    path = file.file.path
    clip = mp_editor.VideoFileClip(path)
    subclip = clip.subclip(segment_num * length, segment_num * length + length)
    subclip.write_videofile(subclip_path, logger=None)
    return FileResponse(open(subclip_path, "rb"), headers={"status": operation_completed_successfully})


def file_processing(file: FileInfo, user: Authentication, analyzed_segment_len=10):
    """
    Analyses file according to chosen parameters and saves results
    @param file: FileInfo instance to analyze
    @param user: Authentication instance, user who uploaded file
    @param analyzed_segment_len: length of segment (in seconds) to analyze
    @return: True if analysis is successful, False if errors occurred
    """
    try:
        file_process = FileProcessingSystem(file, analyzed_segment_len=analyzed_segment_len,
                                            language_flag=language_flag)
        if file.emotionality_flag:
            file_process.get_emotionality()
        if file.gestures_flag:
            file_process.get_gestures()
        if file.clothes_flag:
            file_process.get_clothes()
        if file.angle_flag:
            file_process.get_incorrect_angle()
        if file.glances_flag:
            file_process.get_incorrect_glances()
        if file.clean_speech_flag or file.speech_rate_flag or file.background_noise_flag or file.intelligibility_flag:
            file_process.get_transcription()
            if file.background_noise_flag:
                file_process.get_background_noise()
            if file.speech_rate_flag:
                file_process.get_speech_rate()
            if file.clean_speech_flag:
                file_process.get_filler_words()
            if file.intelligibility_flag:
                file_process.get_intelligibility()
        # search for best interval in file
        save_best_interval(file, user)
        # draw signatures
        file_process.draw()
    except Exception as e:
        logger.debug("File processing error: " + str(e.args))
        return False
    return True


def get_segment_value(file: FileInfo, segment_num):
    """
    Counts real value that corresponds with fragment quality
    @param file: FileInfo instance
    @param segment_num: number of file to count value
    @return:
    """
    final_value = 0
    params_cnt = 0
    file_dict = model_to_dict(file)
    preferred_gestures = [gesture.id - 1 for gesture in file.preferred_gestures.all()]

    for i, name in enumerate(ORDER):
        if file_dict[name + "_flag"]:
            params_cnt += 1
            value = FilePeriodicGrades.objects.get(file_id=file.id, time_period_type=i, period_num=segment_num).value
            if name == "gestures":
                difference = min([abs(preferred_gesture - value) for preferred_gesture in preferred_gestures])
                difference /= 2
            else:
                difference = abs(OPTIMAL_VALUES[name] - value)
            final_value += difference
    if params_cnt == 0:
        return -1
    final_value /= params_cnt
    final_value = round(final_value, 5)
    return final_value


def send_message(email, code):
    """
    Sends email message to confirm email during password recovery
    @param email: user's email to confirm
    @param code: generated four-number code
    """
    from_address = "speaker-trainer@yandex.ru"
    pwd = "qvnasubjnjtqgnnc"
    msg = MIMEText(f"Код для подтверждения почты: {code}.")
    msg["From"] = from_address
    msg["To"] = email
    msg["Subject"] = Header("Подтверждение почты")
    post = smtplib.SMTP_SSL("smtp.yandex.ru")
    post.login(from_address, pwd)
    post.send_message(msg)
    post.quit()


def get_screenshot(file: FileInfo):
    """
    Creates and saves file image (video screenshot)
    @param file: FileInfo instance to get screenshot (first frame)
    """
    path = file.file.path
    clip = mp_editor.VideoFileClip(path)
    image_path = path[:path.rfind('.')] + '.png'
    clip.save_frame(image_path, t=0)


def convert_to_text(data, official: bool):
    """
    Converts real values to text
    @param data: dict with real values for all analysis parameters
    @param official: boolean value, whether file type is official
    @return: dict with text evaluation for each parameter
    """
    new_data = dict()
    for key in data:
        val = data[key]
        if val < 0:
            continue
        if key == "clothes":
            new_val = 2 if val > CONSTANTS[key][0] else 1
            new_val = LANGUAGE[language_flag]["CLOTHES_FLAGS"][new_val]
        else:
            new_val = 0
            constants_key = key
            if key == "neutral_emotionality":
                if official:
                    constants_key = "neutral_emotionality_official"
                else:
                    constants_key = "neutral_emotionality_nonofficial"

            if val > CONSTANTS[constants_key][1]:
                new_val = 3
            elif val > CONSTANTS[constants_key][0]:
                new_val = 2
            elif val > -1:
                new_val = 1
            new_val = LANGUAGE[language_flag]["STATISTICS_FLAGS"][new_val]
        new_data[key] = new_val
    return new_data


def get_user_stats(user_id, get_unknown=False):
    """
    Aggregates values from all user's video files
    @param user_id: user's id to search files
    @param get_unknown: whether to collect default values (-1)
    @return: lists with real values - aggregated files' scores, and list with all user's files ids
    """
    files = FileInfo.objects.filter(user_id=user_id)
    ids_lst = [file.id for file in files]
    data = {field_name: [] for field_name in fields}

    for file in files:
        file_dict = model_to_dict(file)
        for key in file_dict.keys():
            if key in fields:
                if get_unknown or (not get_unknown and file_dict[key] > -0.5):
                    data[key].append(file_dict[key])

    logger.debug("Real values lists: " + str(data))
    logger.debug("Ids list: " + str(ids_lst))
    return data, ids_lst


def save_best_interval(file: FileInfo, user: Authentication):
    """
    Saves best file fragment
    @param file: FileInfo instance to find best fragment
    @param user: Authentication instance to save new best fragment if necessary
    """
    clip = mp_editor.VideoFileClip(file.file.path)
    duration = clip.duration
    length = int(duration // file.analyzed_segment_len)
    best_value = -1
    best_segment_idx = -1
    for i in range(length):
        value = get_segment_value(file, i)
        if value != -1 and (value < best_value or best_value == -1):
            best_value = value
            best_segment_idx = i
    file.best_segment_num = best_segment_idx
    file.best_segment_value = round(best_value, 8)
    file.save()

    # check if new best fragment is better than previous user's best fragment
    old_best_file_idx = user.best_file_num
    if old_best_file_idx != -1:
        old_best_file_value = FileInfo.objects.get(id=old_best_file_idx).best_segment_value
    else:
        old_best_file_value = -1
    if old_best_file_value > best_value or old_best_file_value == -1:
        logger.debug("User's best file index is updated: " + str(file.id))
        user.best_file_num = file.id
        user.save()


def collect_lists(file: FileInfo):
    """
    Creates lists with real values (analysis results on each file fragment) for graphics
    @param file: FileInfo instance to collect analysis results
    @return: dictionary with lists of real values - evaluations on each file fragment
    """
    parameters_list = ORDER
    file_dict = model_to_dict(file)
    values_dict = {}
    for i, name in enumerate(parameters_list):
        if file_dict[name + "_flag"]:
            grades = FilePeriodicGrades.objects.filter(file_id=file.id, time_period_type=i).order_by("period_num")
            values_dict[name + "_timestamps"] = []
            for grade in grades:
                values_dict[name + "_timestamps"].append(grade.value)
    return values_dict


@user_passes_test(lambda u: u.is_superuser)
def main_page(request):
    """
    Creates admin statistics main page
    @return: admin statistics main page (see templates/main_page.html)
    """
    data = {
        "registrations_url": "users_registrations/",
        "parameters_url": "params_usage/?type=percentage"
    }
    return render(request, "main_page.html", context=data)


@user_passes_test(lambda u: u.is_superuser)
def users_registrations(request):
    """
    Creates admin page with line plot (users registration and file uploading)
    @return: admin page with line plot of registration / uploading (see templates/line_chart.html)
    """
    data = get_registrations_data()
    data = {"data": data, "home_page": request.build_absolute_uri('/'), "all_files": FileInfo.objects.all().count(),
            "all_users": Authentication.objects.all().count(),
            "csv_registrations": request.build_absolute_uri('/') + "csv_registrations/"}
    return render(request, "line_chart.html", context=data)


@user_passes_test(lambda u: u.is_superuser)
def parameters_usage_bar_plot(request):
    """
    Creates admin page with bar plot (usage of analysis parameters)
    @return: admin page with bar plot of parameters usage (see templates/bar_chart.html)
    """
    speech_processing_fields = ['emotionality', 'clean_speech', 'speech_rate', 'background_noise', 'intelligibility']
    computer_vision_fields = ['emotionality', 'gestures', 'clothes', 'angle', 'glances']
    colors = ["#5EB344", "#FCB72A", "#F8821A", "#E0393E", "#963D97"]
    all_files = FileInfo.objects.all().count()
    projects_data = {"speech_processing": [], "computer_vision": []}
    coef = 1
    end = ""
    # two modes - in percents and absolute values
    if request.GET.get("type") == "percentage":
        projects_data["button_ref_value"] = "quantity"
        projects_data["button_value"] = "Посмотреть количественные данные"
        projects_data["type_for_text"] = "процентах"
        coef = 100 / all_files
        end = "%"
    elif request.GET.get("type") == "quantity":
        projects_data["button_ref_value"] = "percentage"
        projects_data["button_value"] = "Посмотреть данные в процентах"
        projects_data["type_for_text"] = "целых числах (количестве файлов)"

    for subsystem, name in zip((speech_processing_fields, computer_vision_fields),
                               ("speech_processing", "computer_vision")):
        for parameter, color in zip(subsystem, colors):
            cnt = FileInfo.objects.filter(**{parameter + "_flag": True}).count()
            projects_data[name]. \
                append({"param_name": parameter.replace("_", " "),
                        "param_value": round(cnt / all_files * 100),
                        "param_value_name": str(round(cnt * coef)) + end,
                        "color": color})
    projects_data["all_files"] = all_files
    projects_data["home_page"] = request.build_absolute_uri('/')
    return render(request, "bar_chart.html", context=projects_data)


def csv_registrations(request):
    """
    Creates csv file with dates, registration and file uploading info
    @return: csv file with 5 columns (dates, users per day, total users, files per day, total files)
    """
    data = get_registrations_data()
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="users_activity.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(["Date", "Users_registered", "All_users",
                     "Files_uploaded", "All_files"])
    for row in data:
        writer.writerow(row)
    return response


def get_registrations_data():
    """
    Creates list with main registration and file uploading data (for graphics)
    @return: list of lists with dates and numbers of user registrations and file uploading
    """
    # counting of users for every date
    users = (Authentication.objects
             .values('register_date')
             .annotate(dcount=Count('register_date'))
             .order_by('register_date')
             )
    # counting of files for every date
    files = (FileInfo.objects
             .values('register_date')
             .annotate(dcount=Count('register_date'))
             .order_by('register_date')
             )
    users = list(users)
    files = list(files)
    for file in files:
        file["register_date"] = file["register_date"].date()
    final_files = []
    for file in files:
        if len(final_files) == 0 or final_files[-1]["register_date"] != file["register_date"]:
            final_files.append({"register_date": file["register_date"], "dcount": 0})
        final_files[-1]["dcount"] += 1
    files = final_files
    # earliest date of all
    if users[0]["register_date"] < files[0]["register_date"]:
        min_date = users[0]["register_date"]
    else:
        min_date = files[0]["register_date"]
    # most recent date of all
    if users[-1]["register_date"] > files[-1]["register_date"]:
        max_date = users[-1]["register_date"]
    else:
        max_date = files[-1]["register_date"]
    period = (max_date - min_date).days + 1
    data = [[0] * 5 for _ in range(period)]
    user_idx, file_idx = 0, 0
    # total users and files registered
    total = [0, 0]
    for i in range(period):
        # whether to increase user_list / file_list indexes
        updates = [False, False]
        for lst_idx, lst, data_idx in zip((user_idx, file_idx), (users, files), (1, 3)):
            if lst_idx == len(lst) or (lst[lst_idx]["register_date"] - min_date).days != i:
                data[i][data_idx] = 0
            else:
                data[i][data_idx] = lst[lst_idx]["dcount"]
                updates[data_idx // 2] = True
                total[data_idx // 2] += lst[lst_idx]["dcount"]
            data[i][data_idx + 1] = total[data_idx // 2]
            current_date = min_date + datetime.timedelta(days=i)
            data[i][0] = current_date.strftime("%d.%m.%Y")
        user_idx += updates[0]
        file_idx += updates[1]
    return data

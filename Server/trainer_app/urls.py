from django.urls import path
from . import views

urlpatterns = [
    path("register/email_confirm/", views.register_email_confirm),
    path("register/save/", views.register_save),
    path("login/", views.login),
    path("logout/", views.logout),
    path("password_recovery/email_confirm/", views.password_recovery_email_confirm),
    path("password_recovery/save/", views.password_recovery_save),
    path("upload_file/", views.upload_file),
    path("archive/number_of_files/", views.archive_number_of_files),
    path("archive/file_info/", views.archive_file_info),
    path("archive/file_image/", views.archive_file_image),
    path("modified_file/", views.video_file),
    path("delete_file/", views.delete_file),
    path("file_statistics/", views.file_statistics),
    path("statistics/", views.statistics),
    path("recommendations/all_files/description/", views.user_recommendations_description),
    path("recommendations/all_files/file_fragment/", views.user_recommendations_sample),
    path("recommendations/one_file/description/", views.file_recommendations_description),
    path("recommendations/one_file/file_fragment/", views.file_recommendations_sample),
    path('', views.main_page),
    path('params_usage/', views.parameters_usage_bar_plot),
    path('users_registrations/', views.users_registrations),
    path('csv_registrations/', views.csv_registrations),
]

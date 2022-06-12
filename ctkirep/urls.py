from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from ctkirep import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("reading/", views.ReadingHomeView.as_view(), name="reading_time_home"),
    path("readingupload/", views.reading_time_upload, name="reading_time_upload"),
    path("readingreport/<int:course>", views.ReadingTimeView.as_view(), name="reading_time_report"),
    path("readingexport/", views.reading_time_export, name="reading_time_export"),
    path("progress/", views.PTBaseView.as_view(), name="progress_tests_home"),
    path("progressupload/<int:rtype>", views.content_status_upload, name="pt_upload_status"),
    path("progressupload/<int:rtype>", views.content_status_upload, name="pt_upload_journey"),
    path("progressexport/<int:courseid>", views.csv_export_pt, name="csv_export_pt"),
    path("students", views.StudentsHomeView.as_view(), name='students_home'),
    path("studentslist/<int:course>", views.StudentsTableView.as_view(), name='students_table'),
    path("progressreport/<int:course>", views.PTStatusReportView.as_view(), name="progress_tests_report"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name='ctkirep/login.html'), name='login'),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name='logout'),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(template_name='ctkirep/change_password.html', success_url=reverse_lazy('home')), name='password_change'),
]

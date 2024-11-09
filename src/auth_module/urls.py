from django.urls import path
from . import views

urlpatterns = [
    path("available/", views.AvailableView.as_view(), name="available"),
    path("send-email-otp/", views.EmailSendOTPView.as_view(), name="send_email_otp"),
    path("check-email-otp/", views.check_email_otp, name="check_email_otp"),
    path("log-user/", views.LogEmailView.as_view(), name="log_user"),

]

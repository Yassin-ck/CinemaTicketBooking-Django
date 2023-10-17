
from django.urls import path
from .views import (
    PhoneLogin,
    OtpVerification,
    UserProfileView,
    GoogleSocialAuthView
    )

urlpatterns = [
    path('google/',GoogleSocialAuthView.as_view(),name='google'),
    path("login/", PhoneLogin.as_view(), name="rest_login"),
    path("otp/", OtpVerification.as_view(), name="otp"),
    path('userprofile/',UserProfileView.as_view(),name='userprofile')
]
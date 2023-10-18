
from django.urls import path
from .views import (
    PhoneLogin,
    OtpVerification,
    UserProfileView,
    GoogleSocialAuthView,
    CurrentLocation,
    SearchLocaition
    )

urlpatterns = [
    path('google/',GoogleSocialAuthView.as_view(),name='google'),
    path("login/", PhoneLogin.as_view(), name="rest_login"),
    path("otp/", OtpVerification.as_view(), name="otp"),
    path('userprofile/',UserProfileView.as_view(),name='userprofile'),
    path('currentlocation/',CurrentLocation.as_view(),name='currentlocation'),
    path('searchlocation/',SearchLocaition.as_view(),name='searchlocation')
]
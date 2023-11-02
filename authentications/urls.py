from django.urls import path
from .views import (
    MobilePhoneUpdate,
    OtpVerification,
    UserProfileView,
    GoogleSocialAuthView,
    CurrentLocation,
    EmailAuthAndUpdationView,
    EmailVerification,
)

urlpatterns = [
    path("google/", GoogleSocialAuthView.as_view(), name="google"),
    path("email/", EmailAuthAndUpdationView.as_view(), name="email"),
    path("email/otp/", EmailVerification.as_view(), name="emailotp"),
    path("userprofile/", UserProfileView.as_view(), name="userprofile"),
    path("userprofile/phone/", MobilePhoneUpdate.as_view(), name="phone"),
    path("userprofile/phone/otp/", OtpVerification.as_view(), name="otp"),
    path("currentlocation/", CurrentLocation.as_view(), name="currentlocation"),
]

from django.urls import path
from .views import (
    MobilePhoneUpdate,
    OtpVerification,
    UserProfileView,
    GoogleSocialAuthView,
    CurrentLocation,
    EmailAuthView,
    EmailUpdateView,
    EmailAuthVerification,
    EmailUpdateVerification,
    
)

urlpatterns = [
    path("google/", GoogleSocialAuthView.as_view(), name="google"),
    path("emailauth/", EmailAuthView.as_view(), name="emailauth"),
    path("emailupdate/", EmailUpdateView.as_view(), name="emailupdate"),
    path("emailauth/otp/", EmailAuthVerification.as_view(), name="emailauthotp"),
    path("emailupdate/otp/", EmailUpdateVerification.as_view(), name="emailupdateotp"),
    path("userprofile/", UserProfileView.as_view(), name="userprofile"),
    path("userprofile/phone/", MobilePhoneUpdate.as_view(), name="phone"),
    path("userprofile/phone/otp/", OtpVerification.as_view(), name="otp"),
    path("currentlocation/", CurrentLocation.as_view(), name="currentlocation"),
]

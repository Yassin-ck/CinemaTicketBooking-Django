from django.urls import path
from .views import (
    TheatreOwnerFormApplication,
    TheatreOwnerVerification,
    TheatreLoginRequest,
    TheatreLoginVerify,
    SearchLocaition,
    TheatreRegistration,
    TheatreDetailsView,
    ScreenDetailsForm,
    ScreenSeatArrangementDetails,
)

urlpatterns = [
    path("owner/register/", TheatreOwnerFormApplication.as_view(), name="registration"),
    path("register/", TheatreRegistration.as_view(), name="registration"),
    path("owner/otp/", TheatreOwnerVerification.as_view(), name="otp"),
    path("loginrequest/", TheatreLoginRequest.as_view(), name="loginrequest"),
    path("loginverify/", TheatreLoginVerify.as_view(), name="loginverify"),
    path("searchlocation/", SearchLocaition.as_view(), name="searchlocation"),
    path(
        "theatredetailsview/", TheatreDetailsView.as_view(), name="theatredetailsview"
    ),
    path("screendetailsform/", ScreenDetailsForm.as_view(), name="screendetailsform"),
    path(
        "screendetailsform/<int:pk>/",
        ScreenDetailsForm.as_view(),
        name="screendetailsSingleform",
    ),
    path(
        "screenseatarrange/<int:pk>/",
        ScreenSeatArrangementDetails.as_view(),
        name="screenseatarrange",
    ),
]

from django.urls import path
from .views import (
    TheatreRegistration,
    TheatreVerification,
    TheatreLoginRequest,
    TheatreLoginVerify,
    SearchLocaition
    )
urlpatterns = [
    path('register/',TheatreRegistration.as_view(),name='registration'),
    path('otp/',TheatreVerification.as_view(),name='otp'),
    path('loginrequest/',TheatreLoginRequest.as_view(),name='loginrequest'),
    path('loginverify/',TheatreLoginVerify.as_view(),name='loginverify'),
    path('searchlocation/',SearchLocaition.as_view(),name='searchlocation')

]
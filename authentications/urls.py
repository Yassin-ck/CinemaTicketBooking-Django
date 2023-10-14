from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from django.urls import path
from allauth.socialaccount.views import signup
from .views import OtpLogin,OtpVerification

urlpatterns = [
    path("signup/", signup, name="socialaccount_signup"),
    # path("google/", GoogleLogin.as_view(), name="google_login"),
    path("register/", RegisterView.as_view(), name="rest_register"),
    path("login/", OtpLogin.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("otp/", OtpVerification.as_view(), name="otp"),
]
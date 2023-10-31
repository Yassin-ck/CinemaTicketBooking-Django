from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import TheatreDetails
from authentications.models import MyUser


class TheatreAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user, token = super().authenticate(request)
        if user and token.payload["theatre_email"]:
            return user, token.payload["theatre_email"]
        raise AuthenticationFailed("Custom authentication failed")

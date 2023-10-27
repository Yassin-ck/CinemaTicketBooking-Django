from .models import TheatreDetails
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

class TheatreAuthentication(JWTAuthentication):
    def authenticate(self, request):   
        user, _ = super().authenticate(request)
        if user  and _.payload['theatre_email']:           
            return user ,None 
        raise AuthenticationFailed('Custom authentication failed')
    

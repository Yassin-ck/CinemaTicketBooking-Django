from rest_framework.authentication import BaseAuthentication
from .models import TheatreDetails
from django.db.models import Q

class TheatreAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user = TheatreDetails.objects.filter(Q(id = request.user.theatreownerdetials.theatreowner.id) & Q(is_loginned=True))
        print(user)
        if user is not None:
            return (user,None)
        return None
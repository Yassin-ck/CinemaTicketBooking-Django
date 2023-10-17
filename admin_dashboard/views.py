from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from .serializers import (
    UserProfileViewSerializer,
    )
from rest_framework.views import APIView
from authentications.models import MyUser,UserProfile
from rest_framework.response import Response
# Create your views here.

@permission_classes([IsAdminUser])
class UserProfileViewBYAdmin(APIView):
    def get(self,request):
        user_profile = UserProfile.objects.select_related('user')
        serializer = UserProfileViewSerializer(user_profile,many=True)
        return Response(serializer.data)
    
   
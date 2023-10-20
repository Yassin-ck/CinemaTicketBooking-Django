from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from .serializers import (
    UserProfileViewSerializer,
    RequestedLocationSerializer,
    )
from rest_framework.views import APIView
from authentications.models import (
    MyUser,
    UserProfile,
    RequestLocation,
    )
from rest_framework.response import Response
# Create your views here.

@permission_classes([IsAdminUser])
class UserProfileViewBYAdmin(APIView):
    def get(self,request):
        user_profile = UserProfile.objects.select_related('user')
        serializer = UserProfileViewSerializer(user_profile,many=True)
        return Response(serializer.data)
    

class LocationRequests(APIView):
    def get(self,request):
        requested_location = RequestLocation.objects.filter(status='PENDING')
        serializer = RequestedLocationSerializer(requested_location,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
      
    def patch(self,request,pk=None):
        if pk:
            location = RequestLocation.objects.get(id=pk)
            serializer = RequestedLocationSerializer(location)
            return Response(serializer.data,status=status.HTTP_200_OK)
           
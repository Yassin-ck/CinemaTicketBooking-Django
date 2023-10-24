from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from theatre_dashboard.models import TheareOwnerDetails
from .serializers import (
    UserProfileViewSerializer,
    RequestedLocationSerializer,
    TheatreOwnerDetailsSerializer
    )
from rest_framework.views import APIView
from authentications.models import (
    MyUser,
    UserProfile,
    RequestLocation,
    )
from rest_framework.response import Response
# from authentications.modules.smtp import send_email
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
           
           



class TheatreOwnerRequest(APIView):
    def get(self,request,pk=None):
        if not pk:
            details = TheareOwnerDetails.objects.filter(is_verified=False)
            serializer = TheatreOwnerDetailsSerializer(details,many=True)
        else:
            details = TheareOwnerDetails.objects.get(id=pk)
            serializer = TheatreOwnerDetailsSerializer(details)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    def patch(self,request,pk=None):
        if pk:
            details=TheareOwnerDetails.objects.get(id=pk)
            serializer = TheatreOwnerDetailsSerializer(details, data=request.data, partial=True)
            if serializer.is_valid():
                verification = serializer.validated_data.get('is_verified')
                if verification:
                    return Response({'msg':'verified'},status=status.HTTP_200_OK)
                details.delete()
                return Response({'msg':'Rejected'},status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    


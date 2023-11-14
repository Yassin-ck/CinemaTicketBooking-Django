from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from authentications.modules.smtp import send_email
from django.conf import settings
from rest_framework.views import APIView
from django.db.models import Q
from .pagination import UserProfilePagination
from theatre_dashboard.models import (
    TheareOwnerDetails,
    TheatreDetails,
)
from .serializers import (
    UserProfileViewSerializer,
    RequestedLocationSerializer,
    TheatreOwnerDetailsSerializer,
    TheatreDetailsSerializer,
    TheatreOwnerListSerializer,
    TheatreListSerializer,
)
from authentications.models import (
    UserProfile,
    RequestLocation,
    Location
)

# Create your views here.


@permission_classes([IsAdminUser])
class UserProfileViewBYAdmin(APIView):
    def get(self, request):
        user_profile = UserProfile.objects.select_related("user")
        number_of_users = len(user_profile)
        paginator = UserProfilePagination()
        number_of_page = number_of_users // paginator.page_size
        result_page = paginator.paginate_queryset(user_profile, request)
        serializer = UserProfileViewSerializer(
            result_page, many=True, context={"request": request}
        )
        response_data = {
            "user": serializer.data["features"],
            "page_number": number_of_page,
        }
        return Response(response_data, status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class LocationRequests(APIView):
    def get(self, request):
        requested_location = RequestLocation.objects.filter(status="PENDING")
        serializer = RequestedLocationSerializer(requested_location, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def put(self, request, pk=None):
        if pk:
            location = RequestLocation.objects.get(id=pk)
            serializer = RequestedLocationSerializer(location)
            return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class TheatreOwnerRequest(APIView):
    def get(self, request, pk=None):
        if not pk:
            details = TheareOwnerDetails.objects.filter(
                Q(is_verified=True) & Q(is_approved=False)
            ).only("id", "first_name", "email", "phone", "id_number")
            serializer = TheatreOwnerListSerializer(details, many=True)
        else:
            details = TheareOwnerDetails.objects.get(id=pk)
            serializer = TheatreOwnerDetailsSerializer(details)
        print(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            content_type="multipart/formdata",
        )

    def put(self, request, pk=None):
        if pk:
            details = TheareOwnerDetails.objects.get(id=pk)
            serializer = TheatreOwnerDetailsSerializer(
                details, data=request.data, partial=True
            )
            if serializer.is_valid():
                verification = serializer.validated_data.get("is_approved")
                serializer.save()
                if verification:
                    subject = "Request Approved..."
                    message = """Welcome to BookMyShow....
                    Now you can update your theatre details
                    """
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (details.email,)
                    send_email(subject, message, email_from, recipient_list)
                    return Response({"msg": "verified"}, status=status.HTTP_200_OK)
                else:
                    subject = "Request Rejected..."
                    message = """ 
                    We cant verify your credentials,
                    Please Contact with our customer service or You can use our message system
                    """
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (details.email,)
                    send_email(subject, message, email_from, recipient_list)
                    return Response({"msg": "Rejected"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdminUser])
class TheatreRequest(APIView):
    def get(self, request, pk=None):
        if not pk:
            details = TheatreDetails.objects.filter(is_approved=False).only(
                "id", "theatre_name", "email"
            )
            serializer = TheatreListSerializer(details, many=True)
        else:
            details = TheatreDetails.objects.filter(id=pk).select_related("owner")
            serializer = TheatreDetailsSerializer(details[0])
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None):
        if pk:
            details = TheatreDetails.objects.get(id=pk)
            serializer = TheatreDetailsSerializer(
                details, data=request.data, partial=True
            )
            if serializer.is_valid():
                verification = serializer.validated_data.get("is_approved")
                serializer.save()
                if verification:
                    subject = "Request Approved..."
                    message = """
                    Welcome to BookMyShow....
                    Your Theatre Registration is completed ,
                    Now You can go with you further details ...           
                    """
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (details.email,)
                    send_email(subject, message, email_from, recipient_list)
                    return Response({"msg": "verified"}, status=status.HTTP_200_OK)
                subject = "Theatre Request Rejected..."
                message = """ 
                We cant verify your credentials,
                Please Contact with our customer service or You can use our message system   
                """
                email_from = settings.EMAIL_HOST_USER
                recipient_list = (details.email,)
                send_email(subject, message, email_from, recipient_list)
                return Response({"msg": "Rejected"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




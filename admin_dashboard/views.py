from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from authentications.modules.smtp import send_email
from django.conf import settings
from utils.mapping_variables import UPCOMING,PENDING
from rest_framework.views import APIView
from django.db.models import Q
from .pagination import UserProfilePagination
from theatre_dashboard.models import (
    TheareOwnerDetails,
    TheatreDetails,
)
from theatre_dashboard.serializers import (
    TheatreOwnerListSerializer,
    TheatrOwnerCreateUpdateSerializer,
    TheatreListSerializer,
    TheatreDetailsCreateUpdateSerializer,
    TheatreListChoiceSerializer
)
from authentications.serializers import( 
    UserProfileListSerializer,
    RequestedLocationListSerializer,
    RequestedLocationCreateUpdateSerializer,   
        )

from .serializers import (
    MovieDetailListSerializer,
    MovieDetailsCreateUpdateSerializer,
    MovieDetailsChoiceSerializer
)
from authentications.models import (
    UserProfile,
    RequestLocation
    )
from .models import (
    MoviesDetails,
    Languages
    )
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



@permission_classes([IsAdminUser])
class UserProfileViewBYAdmin(APIView):
    @swagger_auto_schema(
        tags=["Admin View"],
        operation_description="Users Full View",
        responses={
            200:UserProfileListSerializer,
            400:"errors"
        }
    )
    def get(self, request):
        user_profile = UserProfile.objects.select_related("user").order_by("user__username")
        number_of_users = len(user_profile)
        paginator = UserProfilePagination()
        number_of_page = number_of_users // paginator.page_size
        result_page = paginator.paginate_queryset(user_profile, request)
        serializer = UserProfileListSerializer(result_page, many=True, context={"request": request})
        response_data = {
            "user": serializer.data,
            "page_number": number_of_page,
        }
        return Response(response_data, status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class LocationRequests(APIView):
    
    @swagger_auto_schema(
        tags=["Admin View"],
        operation_description="New Location Requests view",
        responses={
            200:RequestedLocationListSerializer,
            500:"Internal errors"
        }
    )
    def get(self, request):
        requested_location = RequestLocation.objects.filter(status=PENDING)
        serializer = RequestedLocationListSerializer(requested_location, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




    @swagger_auto_schema(
        tags=["Admin Verification"],
        operation_description="Accept or Reject New Location Request",
        request_body=RequestedLocationCreateUpdateSerializer,
        responses={
            200:RequestedLocationCreateUpdateSerializer,
            400:"bad request"
        }
    )
    def put(self, request, pk=None):
        if pk:
            location = RequestLocation.objects.get(id=pk)
            serializer = RequestedLocationCreateUpdateSerializer(location)
            return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class TheatreOwnerRequest(APIView):
    @swagger_auto_schema(
        tags=['Admin View'],
        operation_description="New Theatre Owners request View",
        responses={
            200:TheatreOwnerListSerializer,
            404:"not Found",
            500:"internal error",
            400:"bad request"
        })
    def get(self, request, pk=None):
        if not pk:
            details = TheareOwnerDetails.objects.filter(
                Q(is_verified=True) & Q(is_approved=False)
            ).only("id", "first_name", "email", "phone", "id_number")
            serializer = TheatreOwnerListSerializer(details, many=True)
        else:
            try:
                details = TheareOwnerDetails.objects.get(id=pk)
            except:
                return Response({"errors":"No Such Owner request"},status=status.HTTP_404_NOT_FOUND)
            serializer = TheatreOwnerListSerializer(details)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
        
        

    @swagger_auto_schema(
        tags=['Admin Verification'],
        operation_description="New Theatre Owners request Verification",
        request_body=TheatrOwnerCreateUpdateSerializer,
        responses={
            200:TheatrOwnerCreateUpdateSerializer,
            404:"not Found",
            500:"internal error",
            400:"bad request"
        })
    def put(self, request, pk=None):
        if pk:
            details = TheareOwnerDetails.objects.get(id=pk)
            serializer = TheatrOwnerCreateUpdateSerializer(
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
        return Response({"errors":"specify User with id"},status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAdminUser])
class TheatreRequest(APIView):
    @swagger_auto_schema(
        tags=['Admin View'],
        operation_description="New Theatre request View",
        responses={
            200:TheatreListSerializer,
            404:"not Found",
            500:"internal error",
            400:"bad request"
        })
    def get(self, request, pk=None):
        if not pk:
            details = TheatreDetails.objects.filter(is_approved=False).only(
                "id", "theatre_name", "address"
            )
            serializer = TheatreListSerializer(details, many=True)
        else:
            details = TheatreDetails.objects.filter(id=pk).select_related("owner")
            serializer = TheatreListChoiceSerializer(details[0])
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    

    @swagger_auto_schema(
        tags=['Admin Verification'],
        operation_description="New Theatres request Verification",
        request_body=TheatreDetailsCreateUpdateSerializer,
        responses={
            200:TheatreDetailsCreateUpdateSerializer,
            404:"not Found",
            500:"internal error",
            400:"bad request"
        })
    def put(self, request, pk=None):
        if pk:
            details = TheatreDetails.objects.get(id=pk)
            serializer = TheatreDetailsCreateUpdateSerializer(
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


permission_classes([IsAdminUser])
class MovieDetailsAdding(APIView):
    @swagger_auto_schema(
        tags=['Admin View'],
        operation_description="Movies details View",
        responses={
            200:MovieDetailListSerializer,
            404:"not Found",
            500:"internal error",
            400:"bad request"
        })
    def get(self, reqeust, pk=None):
        if not pk:
            movies = MoviesDetails.objects.only("movie_name", "poster")
            serializer = MovieDetailListSerializer(movies, many=True)
        else:
            try:
                movies = MoviesDetails.objects.get(id=pk)
            except:
                return Response({"errors":"Not Available"},status=status.HTTP_404_NOT_FOUND)
            serializer = MovieDetailsChoiceSerializer(movies)
        return Response(serializer.data, status=status.HTTP_200_OK,content_type="multipart/formdata")




    @swagger_auto_schema(
        tags=['Admin Posts'],
        operation_description="New Movie Adding",
        request_body=MovieDetailsCreateUpdateSerializer,
        responses={
            200:MovieDetailsCreateUpdateSerializer,
            500:"internal error",
            400:"bad request"
        })
    def post(self, request):
        print(request.data)
        serializer = MovieDetailsCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            MoviesDetails.objects.create(
                movie_name=serializer.validated_data.get("movie_name"),
                poster=serializer.validated_data.get("poster"),
                director=serializer.validated_data.get("director"),
                status=UPCOMING,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    @swagger_auto_schema(
        tags=['Admin Posts'],
        operation_description="Movie Detials Editing",
        request_body=MovieDetailsCreateUpdateSerializer,
        responses={
            200:MovieDetailsCreateUpdateSerializer,
            500:"internal error",
            400:"bad request",
            404:"Not Found"
        })
    def put(self, request, pk):
            try:
                movies = MoviesDetails.objects.get(id=pk)
            except:
                return Response({"error":"Not Available"},status=status.HTTP_404_NOT_FOUND)
            serializer = MovieDetailsCreateUpdateSerializer(
                movies, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

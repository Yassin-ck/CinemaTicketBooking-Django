from flask import request
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from authentications.modules.smtp import send_email
from django.conf import settings
from rest_framework.views import APIView
from django.db.models import Q
from .pagination import UserProfilePagination
from utils.mapping_variables import (
    UPCOMING,
    PENDING,
    RELEASED,
)
from theatre_dashboard.models import (
    TheareOwnerDetails,
    TheatreDetails,
)
from theatre_dashboard.serializers import (
    TheatreOwnerListSerializer,
    TheatrOwnerCreateUpdateSerializer,
    TheatreListSerializer,
    TheatreDetailsCreateUpdateSerializer,
    TheatreListChoiceSerializer,
)
from authentications.serializers import (
    UserProfileListSerializer,
    RequestedLocationListSerializer,
    RequestedLocationCreateUpdateSerializer,
)

from .serializers import (
    MovieDetailListSerializer,
    MovieDetailsCreateUpdateSerializer,
)
from authentications.models import (
    UserProfile,
    RequestLocation,
)
from .models import (
    Languages,
    MoviesDetails,
)

# swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# celery
from .tasks import send_mail_func
from django.http import HttpResponse


# sending mail through celery
def send_mail_to_all_users(request):
    send_mail_func.delay()
    return HttpResponse("Email has been Sent Successfully")


@permission_classes([IsAdminUser])
class UserProfileViewBYAdmin(APIView):
    @swagger_auto_schema(
        tags=["Admin View"],
        operation_description="Users Full View",
        responses={200: UserProfileListSerializer, 400: "errors"},
    )
    
    def get(self, request):
        instance = UserProfile.objects.select_related("user").order_by("user__username")
        paginator = UserProfilePagination()
        queryset = paginator.paginate_queryset(instance, request)
        serializer = UserProfileListSerializer(
            queryset, many=True, context={"request": request}
        )
        response_data = {
            "user": serializer.data,
            "page_number":paginator.page.paginator.num_pages
            
        }
        return Response(response_data, status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class LocationRequests(APIView):
    @swagger_auto_schema(
        tags=["Admin View"],
        operation_description="New Location Requests view",
        responses={200: RequestedLocationListSerializer, 500: "Internal errors"},
    )
    def get(self, request):
        queryset = RequestLocation.objects.filter(status=PENDING)
        serializer = RequestedLocationListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Admin Verification"],
        operation_description="Accept or Reject New Location Request",
        request_body=RequestedLocationCreateUpdateSerializer,
        responses={200: RequestedLocationCreateUpdateSerializer, 400: "bad request"},
    )
    def put(self, request, pk=None):
        if pk:
            queryset = RequestLocation.objects.get(id=pk)
            serializer = RequestedLocationCreateUpdateSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAdminUser])
class TheatreOwnerRequest(APIView):
    @swagger_auto_schema(
        tags=["Admin View"],
        operation_description="New Theatre Owners request View",
        responses={
            200: TheatreOwnerListSerializer,
            404: "not Found",
            500: "internal error",
            400: "bad request",
        },
    )
    def get(self, request, pk=None):
        if not pk:
            queryset = TheareOwnerDetails.objects.filter(
                Q(is_verified=True) & Q(is_approved=False)
            ).only("id", "first_name", "email", "phone", "id_number")
            serializer = TheatreOwnerListSerializer(queryset, many=True)
        else:
            try:
                queryset = TheareOwnerDetails.objects.get(id=pk)
            except:
                return Response(
                    {"errors": "No Such Owner request"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = TheatreOwnerListSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Admin Verification"],
        operation_description="New Theatre Owners request Verification",
        request_body=TheatrOwnerCreateUpdateSerializer,
        responses={
            200: TheatrOwnerCreateUpdateSerializer,
            404: "not Found",
            500: "internal error",
            400: "bad request",
        },
    )
    def put(self, request, pk=None):
        if pk:
            queryset = TheareOwnerDetails.objects.get(id=pk)
            serializer = TheatrOwnerCreateUpdateSerializer(
                queryset, data=request.data, partial=True
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
                    recipient_list = (queryset.email,)
                    send_email(subject, message, email_from, recipient_list)
                    return Response({"msg": "verified"}, status=status.HTTP_200_OK)
                else:
                    subject = "Request Rejected..."
                    message = """ 
                    We cant verify your credentials,
                    Please Contact with our customer service or You can use our message system
                    """
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (queryset.email,)
                    send_email(subject, message, email_from, recipient_list)
                    return Response({"msg": "Rejected"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"errors": "specify User with id"}, status=status.HTTP_400_BAD_REQUEST
        )


@permission_classes([IsAdminUser])
class TheatreRequest(APIView):
    @swagger_auto_schema(
        tags=["Admin View"],
        operation_description="New Theatre request View",
        responses={
            200: TheatreListSerializer,
            404: "not Found",
            500: "internal error",
            400: "bad request",
        },
    )
    def get(self, request, pk=None):
        if not pk:
            queryset = TheatreDetails.objects.filter(is_approved=False).only(
                "id", "theatre_name", "address"
            )
            serializer = TheatreListSerializer(queryset, many=True)
        else:
            queryset = (
                TheatreDetails.objects.filter(id=pk).select_related("owner").first()
            )
            serializer = TheatreListChoiceSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Admin Verification"],
        operation_description="New Theatres request Verification",
        request_body=TheatreDetailsCreateUpdateSerializer,
        responses={
            200: TheatreDetailsCreateUpdateSerializer,
            404: "not Found",
            500: "internal error",
            400: "bad request",
        },
    )
    def put(self, request, pk=None):
        if pk:
            queryset = TheatreDetails.objects.get(id=pk)
            serializer = TheatreDetailsCreateUpdateSerializer(
                queryset, data=request.data, partial=True
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
                    recipient_list = (queryset.email,)
                    send_email(subject, message, email_from, recipient_list)
                    return Response({"msg": "verified"}, status=status.HTTP_200_OK)
                subject = "Theatre Request Rejected..."
                message = """ 
                We cant verify your credentials,
                Please Contact with our customer service or You can use our message system   
                """
                email_from = settings.EMAIL_HOST_USER
                recipient_list = (queryset.email,)
                send_email(subject, message, email_from, recipient_list)
                return Response({"msg": "Rejected"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


permission_classes([IsAdminUser])


class MovieDetailsAdding(APIView):
    @swagger_auto_schema(
        tags=["Admin View"],
        operation_description="Movies details View",
        responses={
            200: MovieDetailListSerializer,
            404: "not Found",
            500: "internal error",
            400: "bad request",
        },
    )
    def get(self, reqeust, pk=None):
        if not pk:
            queryset = MoviesDetails.objects.filter(~Q(status=RELEASED)).values(
                "id", "movie_name", "director"
            )
        else:
            queryset = MoviesDetails.objects.filter(id=pk).values().first()
            if not queryset:
                return Response(
                    {"errors": "Not Available"}, status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            queryset, status=status.HTTP_200_OK, content_type="multipart/formdata"
        )

    @swagger_auto_schema(
        tags=["Admin Posts"],
        operation_description="New Movie Adding",
        request_body=MovieDetailsCreateUpdateSerializer,
        responses={
            200: MovieDetailsCreateUpdateSerializer,
            500: "internal error",
            400: "bad request",
        },
    )
    def post(self, request):
        print(request.data)
        serializer = MovieDetailsCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            MoviesDetails.objects.create(
                movie_name=serializer.validated_data.get("movie_name"),
                poster=serializer.validated_data.get("poster"),
                director=serializer.validated_data.get("director"),
                status=UPCOMING,
            )
            send_mail_to_all_users(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Admin Posts"],
        operation_description="Movie Detials Editing",
        request_body=MovieDetailsCreateUpdateSerializer,
        responses={
            200: MovieDetailsCreateUpdateSerializer,
            500: "internal error",
            400: "bad request",
            404: "Not Found",
        },
    )
    def put(self, request, pk):
        try:
            movies = MoviesDetails.objects.get(id=pk)
        except:
            return Response(
                {"error": "Not Available"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = MovieDetailsCreateUpdateSerializer(
            movies, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MoviesListing(APIView):
    def get(self, request):
        queryset = (
            MoviesDetails.objects.filter(~Q(status=RELEASED))
            .values()
            .order_by("-id")[:8]
        )
        return Response(queryset, status=status.HTTP_200_OK)

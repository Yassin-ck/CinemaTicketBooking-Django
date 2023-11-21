from django.shortcuts import render
from rest_framework.views import APIView
from authentications.modules.utils import send_sms, verify_user_code
from rest_framework.response import Response
from rest_framework import status
from authentications.modules.smtp import send_email
from django.conf import settings
from authentications import views
from django.db.models import Q
import random, math
from rest_framework.decorators import permission_classes
from .theatre_auth import TheatreAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from utils.mapping_variables import row_alpha
from authentications.serializers import (
    LocationListSerializer,
    RequestedLocationCreateUpdateSerializer,
    OtpSerilizers
)
from .serializers import (
    TheatreDetailsCreateUpdateSerializer,
    TheatrOwnerCreateUpdateSerializer,
    ScreenDetailsListSerializer,
    ScreenDetailsCreateUpdateSerailizer,
    TheatreListSerializer,
    ScreenSeatArrangementListSerailizer,
    ScreenSeatArrangementCreateUpdateSerailizer
)
from authentications.models import (
    MyUser,
    RequestLocation,
    Location
)
from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    ScreenDetails,
    ScreenSeatArrangement,
)
from drf_yasg.utils import swagger_auto_schema

@permission_classes([IsAuthenticated])
class TheatreOwnerFormApplication(APIView):
    @swagger_auto_schema(
        tags=["Theatre Owner"],
        operation_description="Application Form for TheatreOwners",
        request_body=TheatrOwnerCreateUpdateSerializer,
        responses={
            201:TheatrOwnerCreateUpdateSerializer,
            400:"bad request"
        }
    )
    def post(self, request):
        serializer = TheatrOwnerCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user = TheareOwnerDetails.objects.create(
                user=request.user,
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                email=serializer.validated_data.get("email"),
                phone=serializer.validated_data.get("phone"),
                alternative_contact=serializer.validated_data.get(
                    "alternative_contact"
                ),
                id_proof=serializer.validated_data.get("id_proof"),
                id_number=serializer.validated_data.get("id_number"),
                address=serializer.validated_data.get("address"),
            )
            verification_sid = send_sms(user.phone)
            return Response(
                {"verification_sid": verification_sid, "msg": "Otp Sent Succesfully"},
                status=status.HTTP_201_CREATED,
            )
        print(serializer.errors)
        return Response(
            {"msg": "Wrong", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


@permission_classes([IsAuthenticated])
class TheatreOwnerVerification(APIView):
    @swagger_auto_schema(
        tags=["Theatre Owner"],
        operation_description="Verifiying Phone Number,ignore email and otp fields in the body",
        request_body=OtpSerilizers,
        responses={
            200:OtpSerilizers,
            400:"bad request"
        })
    def post(self, request):
        verification_sid = request.data.get("verification_sid")
        otp_entered = request.data.get("otp_entered")
        serializer = OtpSerilizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        verify_status = verify_user_code(verification_sid, otp_entered)
        if verify_status is not None and verify_status.status == "approved":
            try:
                user = TheareOwnerDetails.objects.get(user=request.user)
                user.is_verified = True
                user.save()
                subject = "New Theatre Request"
                message = "New theatre is requested.. check it out !!!"
                email_from = user.email
                recipient_list = (settings.EMAIL_HOST_USER,)
                send_email(subject, message, email_from, recipient_list)
                return Response({"msg": "Success"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"msg": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg": "error"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
class TheatreRegistration(APIView):
    @swagger_auto_schema(
        tags=["Theatres"],
        operation_description="Application Form for Theatre details",
        request_body=TheatreDetailsCreateUpdateSerializer,
        responses={
            201:TheatreDetailsCreateUpdateSerializer,
            400:"bad request"
        })
    def post(self, request):
        serializer = TheatreDetailsCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            theatre = TheatreDetails.objects.create(
                owner=TheareOwnerDetails.objects.get(
                    Q(user=request.user) & Q(is_approved=True)
                ),
                theatre_name=serializer.validated_data.get("theatre_name"),
                email=serializer.validated_data.get("email"),
                phone=serializer.validated_data.get("phone"),
                alternative_contact=serializer.validated_data.get(
                    "alternative_contact"
                ),
                address=serializer.validated_data.get("address"),
                location=serializer.validated_data.get("location"),
                num_of_screens=serializer.validated_data.get("num_of_screens"),
                certification=serializer.validated_data.get("certification"),
            )
            subject = "New theatre request...."
            message = "new theatre request. check it out..."
            email_from = theatre.email
            recipient_list = (settings.EMAIL_HOST_USER,)
            send_email(subject, message, email_from, recipient_list)
            return Response({"msg": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
class TheatreLoginRequest(APIView):
    @swagger_auto_schema(
        tags=["Theatres"],
        operation_description="TheatreLogin interface",
        request_body=TheatreDetailsCreateUpdateSerializer,
        responses={
            201:TheatreDetailsCreateUpdateSerializer,
            400:"bad request"
        })
    
    def post(self, request):
        email = request.data.get("email")
        try:
            otp = math.floor(random.randint(100000, 999999))
            subject = "Otp Verification"
            message = f"Your Otp for login : {otp}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = (email,)
            send_email(subject, message, email_from, recipient_list)
            response_data = {"email": email, "otp": otp, "msg": "Check Email......"}
            return Response(response_data, status=status.HTTP_200_OK)
        except:
            return Response(
                {"msg": "Something Went Wrong..."}, status=status.HTTP_400_BAD_REQUEST
            )


@permission_classes([IsAuthenticated])
class TheatreLoginVerify(APIView):
    @swagger_auto_schema(
        tags=["Theatres"],
        operation_description="Otp Verification For Theatre AUthentication",
        request_body=OtpSerilizers,
        responses={
            200:OtpSerilizers,
            400:"bad request"
        })
    def post(self, request):
        print(request.data)
        otp = request.data.get("otp")
        otp_entered = request.data.get("otp_entered")
        email = request.data.get("email")
        serializer = OtpSerilizers(data=request.data)
        if serializer.is_valid():
            if otp == otp_entered:
                try:
                    theatre = TheatreDetails.objects.get(
                        Q(email=email) & Q(is_approved=True)
                    )
                    token = views.get_tokens_for_user(theatre.owner.user, email)
                    return Response(
                        {"msg": "loginned", "token": token}, status=status.HTTP_200_OK
                    )
                except MyUser.DoesNotExist:
                    return Response({"msgt": "You are not Verified.."})
            return Response({"msg": "invalid otp.."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticatedOrReadOnly])
class SearchLocaition(APIView):
    @swagger_auto_schema(
        tags=["location"],
        operation_description="Search the Location Here",
        responses={
            200:LocationListSerializer,
            400:"bad request",
            404:"not found"
        })
    def get(self, request):
        q = request.GET.get("q")
        if len(q) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Q_base = Q(district__icontains=q) | Q(place__icontains=q)
        location_data = Location.objects.filter(Q_base)
        if location_data:
            serializer = LocationListSerializer(location_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"msg": "Location not found..."}, status=status.HTTP_404_NOT_FOUND
        )
        
        
        
    

    @swagger_auto_schema(
        tags=["location"],
        operation_description="New Location request",
        request_body=RequestedLocationCreateUpdateSerializer,
        responses={
            200:RequestedLocationCreateUpdateSerializer,
            400:"bad request",
        })
    def post(self, request):
        serializer = RequestedLocationCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                RequestLocation.objects.create(
                    user=request.user,
                    country=serializer.validated_data.get("country"),
                    state=serializer.validated_data.get("state"),
                    district=serializer.validated_data.get("district"),
                    place=serializer.validated_data.get("place"),
                )
                subject = "New Location Requested"
                message = "New location request, check it out ......."
                email_from = request.user.email
                recipient_list = (settings.EMAIL_HOST_USER,)
                send_email(subject, message, email_from, recipient_list)

            except:
                return Response({"msg": "Something went wrong`"})
            return Response(
                {"msg": "Your location will be updated soon..."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TheatreAuthentication])
class TheatreDetailsView(APIView):
    @swagger_auto_schema(
        tags=["Theatres"],
        operation_description="Theatre Details View For Theatres",
        responses={
            200:TheatreListSerializer,
            404:"not found"
        })
    def get(self, request):
        theatre = TheatreDetails.objects.filter(owner__user=request.user)
        if theatre:
            serializer = TheatreListSerializer(theatre, many=True)
            return Response({"theatre": serializer.data},status=status.HTTP_200_OK)
        return Response({"error":"Something Went Wrong"},status=status.HTTP_404_NOT_FOUND)


@authentication_classes([TheatreAuthentication])
class ScreenDetailsForm(APIView):
    @swagger_auto_schema(
        tags=["Screen"],
        operation_description="Screen Details View For Theatres",
        responses={
            200:ScreenDetailsListSerializer,
            400:"Bad Request"
        })
    def get(self, request, pk=None):
        if not pk:
            screen_details = ScreenDetails.objects.filter(theatre__email=request.auth)
            serializer = ScreenDetailsListSerializer(screen_details, many=True)
        else:
            screen_details = ScreenDetails.objects.get(
                Q(id=pk) & Q(theatre__email=request.auth)
            )
            serializer = ScreenDetailsListSerializer(screen_details)
        return Response({"screens": serializer.data}, status=status.HTTP_200_OK)
    
    

    @swagger_auto_schema(
        tags=["Screen"],
        operation_description="Screen Details updation",
        request_body=ScreenDetailsCreateUpdateSerailizer,
        responses={
            200:ScreenDetailsCreateUpdateSerailizer,
            400:"Bad Request"
        })
    def put(self, request, pk=None):
        if pk is not None:
            screen_detail = ScreenDetails.objects.get(
                Q(id=pk) & Q(theatre__email=request.auth)
            )
            serializer = ScreenDetailsCreateUpdateSerailizer(
                screen_detail, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TheatreAuthentication])
class ScreenSeatArrangementDetails(APIView):
    @swagger_auto_schema(
        tags=["SeatArrangements"],
        operation_description="Screen Seats view ",
        responses={
            200:ScreenSeatArrangementListSerailizer,
            400:"Bad Request"
        })
    def get(self, request, pk=None):
        if pk:
            seat_arrange = (
                ScreenSeatArrangement.objects.filter(
                    Q(screen_id=pk) & Q(screen__theatre__email=request.auth)
                )
                .select_related("screen")
                .first()
            )
            if not seat_arrange.seating:
                screen_detail = seat_arrange.screen
                row_number = screen_detail.row_count
                column = screen_detail.column_count       
                row = [j for i, j in zip(range(1, row_number + 1), row_alpha)]
                Seating_arrangement = [
                    f"{j}{i}" for i in range(1, column + 1) for j in row
                ]
                sorted_seating = sorted(Seating_arrangement, key=lambda x: (x[0]))
                seat_arrange.seating = sorted_seating
                seat_arrange.save()
            serializer = ScreenSeatArrangementListSerailizer(seat_arrange)
            return Response({"screens": serializer.data}, status=status.HTTP_200_OK)
        return Response({"msg": "specify the id"}, status=status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(
        tags=["SeatArrangements"],
        operation_description="Screen Seats Updations ",
        request_body=ScreenSeatArrangementCreateUpdateSerailizer,
        responses={
            200:ScreenSeatArrangementCreateUpdateSerailizer,
            400:"Bad Request"
        })
    def put(self, request, pk=None):
        if pk is not None:
            seat_arrangements = (
                ScreenSeatArrangement.objects.filter(
                    Q(screen_id=pk) & Q(screen__theatre__email=request.auth)
                )
                .select_related("screen")
                .first()
            )
            screen_details = seat_arrangements.screen
            serializer = ScreenSeatArrangementCreateUpdateSerailizer(
                seat_arrangements, data=request.data, partial=True
            )

            if serializer.is_valid():
                instance = serializer.instance
                instance.seating = serializer.validated_data.get(
                    "seating", instance.seating
                )
                instance.save()
                Number_of_seats = len(serializer.data.get("seating"))
                seat_arrangements.is_approved = (
                    Number_of_seats == screen_details.number_of_seats
                )
                seat_arrangements.save()
                return Response(
                    {
                        "msg": "Update successful",
                        "data": serializer.data,
                        "is_approved": seat_arrangements.is_approved,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"errors":"specify the id"}, status=status.HTTP_400_BAD_REQUEST)



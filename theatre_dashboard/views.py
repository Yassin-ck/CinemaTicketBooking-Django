from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authentications.modules.smtp import send_email
from django.conf import settings
from authentications import views
from django.core.cache import cache
import random, math
from .theatre_auth import TheatreAuthentication
from authentications.modules.utils import (
    send_sms,
    verify_user_code
    )
from django.db.models import (
    Q,
    F
    )
from admin_dashboard.models import (
    Languages,
    MoviesDetails
    )
from rest_framework.decorators import (
    permission_classes,
    authentication_classes
    )
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, 
    IsAuthenticated
    )
from utils.mapping_variables import (
    RELEASED,
    row_alpha,
    TIME,
    DATES,
    MOVIE,
    LANGUAGE,
    today,
    CACHE_PREFIX_THEATRE_AUTH,
    )
from authentications.serializers import (
    LocationListSerializer,
    RequestedLocationCreateUpdateSerializer,
    OtpSerilizers,
    EmailSerilaizer,
    )
from .serializers import (
    TheatreDetailsCreateUpdateSerializer,
    TheatrOwnerCreateUpdateSerializer,
    ScreenDetailsListSerializer,
    ScreenDetailsCreateUpdateSerailizer,
    TheatreListSerializer,
    ScreenSeatArrangementListSerailizer,
    ShowCreateUpdateSerialzer,
    ShowsListSerializer,
    )
from authentications.models import (
    RequestLocation,
    Location
    )
from .models import (
    ShowDates,
    ShowTime,
    TheareOwnerDetails,
    TheatreDetails,
    ScreenDetails,
    ScreenSeatArrangement,
    Shows,
    )
#swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@permission_classes([IsAuthenticated])
class TheatreOwnerFormApplication(APIView):
    @swagger_auto_schema(
        tags=["Theatre Owner"],
        operation_description="Application Form for TheatreOwners",
        request_body=TheatrOwnerCreateUpdateSerializer,
        responses={201: TheatrOwnerCreateUpdateSerializer, 400: "bad request"},
    )
    def post(self, request):
        serializer = TheatrOwnerCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            queryset = TheareOwnerDetails.objects.create(
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
            verification_sid = send_sms(queryset.phone)
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
        responses={200: OtpSerilizers, 400: "bad request"},
    )
    def post(self, request):
        verification_sid = request.data.get("verification_sid")
        otp_entered = request.data.get("otp_entered")
        serializer = OtpSerilizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        verify_status = verify_user_code(verification_sid, otp_entered)
        if verify_status is not None and verify_status.status == "approved":
            try:
                queryset = TheareOwnerDetails.objects.get(user=request.user)
                queryset.is_verified = True
                queryset.save()
                subject = "New Theatre Request"
                message = "New theatre is requested.. check it out !!!"
                email_from = queryset.email
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
        responses={201: TheatreDetailsCreateUpdateSerializer, 400: "bad request"},
    )
    def post(self, request):
        serializer = TheatreDetailsCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            queryset = TheatreDetails.objects.create(
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
            email_from = queryset.email
            recipient_list = (settings.EMAIL_HOST_USER,)
            send_email(subject, message, email_from, recipient_list)
            token = views.get_tokens_for_user(queryset.owner.user, queryset.email)
            return Response(
                {"msg": "success", "token": token}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
class TheatreLoginRequest(APIView):
    @swagger_auto_schema(
        tags=["Theatres"],
        operation_description="TheatreLogin interface",
        request_body=EmailSerilaizer,
        responses={201: TheatreDetailsCreateUpdateSerializer, 400: "bad request"},
    )
    def post(self, request):
        serializer = EmailSerilaizer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            try:
                otp = math.floor(random.randint(100000, 999999))
                subject = "Otp Verification"
                message = f"Your Otp for login : {otp}"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = (email,)
                send_email(subject, message, email_from, recipient_list)
                response_data = {"email": email, "otp": otp}
                cache.set(f"{CACHE_PREFIX_THEATRE_AUTH}_{email}", response_data, None)
                return Response(response_data, status=status.HTTP_200_OK)
            except:
                return Response(
                    {"msg": "Something Went Wrong..."},
                    status=status.HTTP_400_BAD_REQUEST,
                )


@permission_classes([IsAuthenticated])
class TheatreLoginVerify(APIView):
    @swagger_auto_schema(
        tags=["Theatres"],
        operation_description="Otp Verification For Theatre AUthentication",
        request_body=OtpSerilizers,
        responses={200: OtpSerilizers, 400: "bad request"},
    )
    def post(self, request):
        email = request.data.get("email")
        cached_auth_data = cache.get(f"{CACHE_PREFIX_THEATRE_AUTH}_{email}")
        if cached_auth_data is not None:
            otp = cached_auth_data.get("otp")
            email = cached_auth_data.get("email")
            otp_entered = request.data.get("otp_entered")
            serializer = OtpSerilizers(data=request.data)
            if serializer.is_valid():
                if int(otp) == int(otp_entered):
                    try:
                        queryset = (
                            TheatreDetails.objects.filter(
                                Q(email=email) & Q(is_approved=True)
                            )
                            .prefetch_related("screen_details__screenseatarrangement")
                            .first()
                        )
                        if queryset:
                            theatre = True
                            token = views.get_tokens_for_user(
                                queryset.owner.user, theatre, email
                            )
                        else:
                            return Response(
                                {"msg": "You Are Not Authorized"},
                                status=status.HTTP_401_UNAUTHORIZED,
                            )
                        datas = [
                            i.id
                            for i in queryset.screen_details.all()
                            if i.is_approved == False
                        ]
                        if not datas:
                            return Response(
                                {"msg": "loginned", "token": token},
                                status=status.HTTP_200_OK,
                            )
                        return Response(
                            {
                                "warning": "Continue With your Updation",
                                "id": datas[0],
                                "token": token,
                            },
                            status=status.HTTP_403_FORBIDDEN,
                        )
                    except TheatreDetails.DoesNotExist:
                        return Response({"msg": "You are not Verified.."})
                return Response(
                    {"msg": "invalid otp.."}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": ".."}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticatedOrReadOnly])
class SearchLocaition(APIView):
    @swagger_auto_schema(
        tags=["location"],
        operation_description="Search the Location Here",
        responses={200: LocationListSerializer, 400: "bad request", 404: "not found"},
    )
    def get(self, request):
        q = request.GET.get("q")
        if len(q) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Q_base = Q(district__istartswith=q) | Q(place__istartswith=q)
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
            200: RequestedLocationCreateUpdateSerializer,
            400: "bad request",
        },
    )
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
@permission_classes([IsAuthenticated])
class TheatreDetailsView(APIView):
    @swagger_auto_schema(
        tags=["Theatres"],
        operation_description="Theatre Details View For Theatres",
        responses={200: TheatreListSerializer, 404: "not found"},
    )
    def get(self, request):
        queryset = TheatreDetails.objects.filter(owner__user=request.user)
        if queryset:
            serializer = TheatreListSerializer(queryset, many=True)
            return Response({"theatre": serializer.data}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Something Went Wrong"}, status=status.HTTP_404_NOT_FOUND
        )


@authentication_classes([TheatreAuthentication])
class ScreenDetailsForm(APIView):
    @swagger_auto_schema(
        tags=["Screen"],
        operation_description="Screen Details View For Theatres",
        responses={200: ScreenDetailsListSerializer, 400: "Bad Request"},
    )
    def get(self, request, pk=None):
        if pk:
            queryset = self.get_object(request, pk)
        else:
            queryset = ScreenDetails.objects.filter(
                theatre__email=request.auth
            ).values()
        return Response(queryset, status=status.HTTP_200_OK)

    def get_object(self, request, pk):
        return (
            ScreenDetails.objects.filter(Q(id=pk) & Q(theatre__email=request.auth))
            .values()
            .first()
        )

    @swagger_auto_schema(
        tags=["Screen"],
        operation_description="Screen Details updation",
        request_body=ScreenDetailsCreateUpdateSerailizer,
        responses={200: ScreenDetailsCreateUpdateSerailizer, 400: "Bad Request"},
    )
    def put(self, request, pk=None):
        print(request.data)
        if pk is not None:
            queryset = (
                ScreenDetails.objects.filter(Q(id=pk) & Q(theatre__email=request.auth))
                .select_related("theatre")
                .first()
            )
            serializer = ScreenDetailsCreateUpdateSerailizer(
                queryset, data=request.data, partial=True
            )
            if serializer.is_valid():
                queryset.theatre.is_verified = True
                queryset.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TheatreAuthentication])
@permission_classes([IsAuthenticated])
class ScreenSeatArrangementDetails(APIView):
    @swagger_auto_schema(
        tags=["SeatArrangements"],
        operation_description="Screen Seats view ",
        responses={200: ScreenSeatArrangementListSerailizer, 400: "Bad Request"},
    )
    def get(self, request, pk=None):
        if pk:
            queryset = (
                ScreenSeatArrangement.objects.filter(
                    Q(screen_id=pk) & Q(screen__theatre__email=request.auth)
                )
                .select_related("screen")
                .first()
            )
            screen_detail = queryset.screen
            if not queryset.seating:
                self.seatArrangement(screen_detail, queryset)
            else:
                if len(queryset.seating) != screen_detail.row_count:
                    queryset.seating = []
                    queryset.save()
                    self.seatArrangement(screen_detail, queryset)
            serializer = ScreenSeatArrangementListSerailizer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"msg": "specify the id"}, status=status.HTTP_400_BAD_REQUEST)

    def seatArrangement(self, screen_detail, queryset):
        row_number = screen_detail.row_count
        column = screen_detail.column_count
        row = [j for i, j in zip(range(1, row_number + 1), row_alpha)]
        Seating_arrangement = [
            [f"{row}{i}" for i in range(1, column + 1)]
            for row in row_alpha[:row_number]
        ]
        sorted_seating = sorted(Seating_arrangement, key=lambda x: (x[0]))
        queryset.seating = sorted_seating
        queryset.save()
        return


@authentication_classes([TheatreAuthentication])
@permission_classes([IsAuthenticated])
class ShowUpdatesToTheatres(APIView):
    @swagger_auto_schema(
        tags=["ShowsUpdating"],
        operation_description="This is the view for showing all the shows",
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "show_time__time": openapi.Schema(type=openapi.TYPE_STRING),
                            "language__name": openapi.Schema(type=openapi.TYPE_STRING),
                            "moies__movie_name": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, screen_id, date=None, show_id=None, time=None):
        Q_Base = Q(screen__theatre__email=request.auth) & Q(screen_id=screen_id)
        if date and screen_id and show_id and time:
            Q_Base &= (
                Q(show_dates__dates=date) & Q(id=show_id) & Q(show_time__time=time)
            )
            queryset = (
                Shows.objects.filter(Q_Base)
                .select_related("movies", "language")
                .first()
            )
            serializer = ShowsListSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif date and screen_id:
            Q_Base &= Q(show_dates__dates=date)
            queryset = Shows.objects.filter(Q_Base).values(
                "id",
                time=F("show_time__time"),
                languages=F("language__name"),
                movie=F("movies__movie_name"),
            )
        elif screen_id:
            Q_Base &= Q(show_dates__dates__gte=today)
            queryset = (
                Shows.objects.filter(Q_Base)
                .values(date=F("show_dates__dates"))
                .distinct("show_dates__dates")
                .order_by("-show_dates__dates")
            )
        return Response(queryset, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ShowCreateUpdateSerialzer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            queryset = Shows.objects.get(
                Q(id=pk) & Q(screen__theatre__email=request.auth)
            )
        except Shows.DoesNotExist:
            return Response({"msg": "Not Permitted..."})
        serializer = ShowCreateUpdateSerialzer(
            queryset, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TheatreAuthentication])
@permission_classes([IsAuthenticated])
class ShowDetailsForUpdating(APIView):
    def get(self, request, screen_id):
        q = request.GET.get("q")
        if q == MOVIE:
            queryset = self.get_model_data(MoviesDetails, ~Q(status=RELEASED))
        elif q[:5] == DATES:
            time_data = [int(i) for i in q.split(",")[1:]]
            show = Shows.objects.filter(
                Q(screen_id=screen_id)
                & Q(show_dates__dates__gt=today)
                & Q(show_time__id__in=time_data)
            ).values(date=F("show_dates__dates"))
            dates_to_exclude = [i["date"] for i in show]
            Q_Base = Q(dates__gt=today) & ~Q(dates__in=dates_to_exclude)
            queryset = self.get_model_data(ShowDates, Q_Base)
        elif q[:8] == LANGUAGE:
            show = Shows.objects.filter(
                Q(screen_id=screen_id)
                & Q(show_dates__dates__gt=today)
                & Q(movies_id=q[8:])
            ).values("language_id")
            language_to_exclude = [i["language_id"] for i in show]
            queryset = self.get_model_data(Languages, ~Q(id__in=language_to_exclude))
        elif q == TIME:
            queryset = self.get_model_data(ShowTime)
        return Response({"data": queryset}, status=status.HTTP_200_OK)

    def get_model_data(self, Models, *filters):
        return Models.objects.filter(*filters).values()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import status
from ipware import get_client_ip
from django.core.cache import cache
from django.contrib.gis.geos import Point
from authentications.modules.smtp import send_email
import urllib, json
from django.conf import settings
from threading import Thread
from authentications.modules.utils import send_sms, verify_user_code  # twilio
import random, math
from drf_yasg.utils import swagger_auto_schema
from theatre_dashboard.models import TheareOwnerDetails
from utils.mapping_variables import (
    CACHE_PREFIX_EMAIL_AUTHENTICATION,
    CACHE_PREFIX_EMAIL_UPDATION,
    CACHE_PREFIX_MOBILE_UPDATION
    )
from rest_framework.permissions import (
    IsAuthenticated,
)
from .models import (
    MyUser,
    UserProfile,
    Location,
)
from .serializers import (
    EmailSerilaizer,
    UserProfilePhoneSerializer,
    UserEmailSerializer,
    MyTokenSerializer,
    UserProfileListSerializer,
    GoogleSocialAuthSerializer,
    OtpSerilizers
)




# JWTToken
def get_tokens_for_user(user,theatre, *args):
    token = MyTokenSerializer.get_token(user,theatre, *args)

    return {
        "refresh": str(token),
        "access": str(token.access_token),
    }


class GoogleSocialAuthView(APIView):
    def post(self, request):
        serializer = GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = (serializer.validated_data)["auth_token"]
        return Response(data, status=status.HTTP_200_OK)


class CurrentLocation(APIView):
    @swagger_auto_schema(
        operation_description=" current location of user",    
    )
    def get(self, request):
        try:
            client_ip, is_routable = get_client_ip(request)
            if client_ip is None:
                client_ip = "0.0.0.0"
            else:
                if is_routable:
                    ip_type = "public"
                else:
                    ip_type = "private"
            print(ip_type, client_ip)
            auth = settings.IP_AUTH
            ip_address = "103.70.197.189"  # for checking
            url = f"https://api.ipfind.com/?auth={auth}&ip={ip_address}"
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            data["client_ip"] = client_ip
            data["ip_type"] = ip_type
            point = Point(data["longitude"], data["latitude"])
            if not Location.objects.filter(coordinates=point).exists():
                Location.objects.create(
                    country=data["country"],
                    state=data["region"],
                    district=data["county"],
                    place=data["city"],
                    coordinates=point,
                )
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response({"error":"Something Went Wrong.."}, status=status.HTTP_404_NOT_FOUND)


class EmailAuthView(APIView):
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="For Email Authentication And Email Updation after Authentication",
        request_body=UserEmailSerializer,
        responses={
            200:UserEmailSerializer,
            400:"bad request",
            500:"errors"
        })
    def post(self, request):
        email = request.data.get("email")
        serializer = EmailSerilaizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = math.floor((random.randint(100000, 999999)))
        subject = "Otp for account verification"
        message = f"Your otp for account verification {otp}"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (email,)
        email_thread = Thread(
            target=send_email, args=(subject, message,email_from, recipient_list)  
        )
        email_thread.start()   
        response_data = {"email": email, "otp": otp}
        cache.set(f"{CACHE_PREFIX_EMAIL_AUTHENTICATION}_{email}",response_data,30)
        return Response({"msg":"chaeck your email...."}, status=status.HTTP_200_OK)



@permission_classes([IsAuthenticated])
class EmailUpdateView(APIView):
    @swagger_auto_schema(
       tags=["ProfileUpdation"],
        operation_description="Email Updation By User",
        responses={
            200:UserEmailSerializer,
            400:"bad request",
            500:"errors"
        })
    def get(self, request):
        return Response({"email": request.user.email}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
       tags=["ProfileUpdation"],  
        operation_description="For Email Authentication And Email Updation after Authentication",
        request_body=UserEmailSerializer,
        responses={
            200:UserEmailSerializer,
            400:"bad request",
            500:"errors"
        })
    def post(self, request):
        email = request.data.get("email")
        if email == request.user.email:
            return Response({"msg": "No Changes"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = math.floor((random.randint(100000, 999999)))
        subject = "Otp for account verification"
        message = f"Your otp for account verification {otp}"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = (email,)
        email_thread = Thread(
            target=send_email, args=(subject, message, email_from, recipient_list)
        )
        email_thread.start()
        response_data = {"email": email, "otp": otp}
        cache.set(f"{CACHE_PREFIX_EMAIL_UPDATION}_{email}",response_data,30)
        return Response(response_data, status=status.HTTP_200_OK)




class EmailAuthVerification(APIView):
    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Otp Verification For Authentication And Mobile Updation",
        request_body=OtpSerilizers,
        responses={
            200:OtpSerilizers,
            400:"bad request",
            500:'errors'
        })
    def post(self, request):
        email_enterd = request.data.get('email')
        cached_auth_data = cache.get(f"{CACHE_PREFIX_EMAIL_AUTHENTICATION}_{email_enterd}")
        if cached_auth_data is not None:
            otp = cached_auth_data.get('otp')
            email = cached_auth_data.get('email')
            otp_entered = request.data.get("otp_entered")
            serializer = OtpSerilizers(data=request.data)
            if serializer.is_valid():
                if int(otp) == int(otp_entered):
                    user,_ = MyUser.objects.get_or_create(email=email)
                    theatre = None
                    try:
                        theatre = TheareOwnerDetails.objects.get(user_id=user.id)
                    except TheareOwnerDetails.DoesNotExist:
                        pass 
                    token = get_tokens_for_user(user,theatre)
                    return Response({"token": token}, status=status.HTTP_200_OK)
                return Response({"msg": "Invalid Otp..."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg":"something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        



@permission_classes([IsAuthenticated])
class EmailUpdateVerification(APIView):
    @swagger_auto_schema(
        tags=["ProfileUpdation"],
        operation_description="Otp Verification For Authentication And Mobile Updation",
        request_body=OtpSerilizers,
        responses={
            200:OtpSerilizers,
            400:"bad request",
            500:'errors'
        })
    def post(self, request):
        email_enterd = request.data.get('email')
        cached_update_data = cache.get(f"{CACHE_PREFIX_EMAIL_UPDATION}_{email_enterd}")
        if cached_update_data is not None:
            otp = cached_update_data.get("otp")
            email = cached_update_data.get("email")
            otp_entered = request.data.get("otp_entered")
            serializer = OtpSerilizers(data=request.data)
            if serializer.is_valid():
                if int(otp) == int(otp_entered):
                    user = request.user
                    user.email = email
                    user.save()
                    return Response({"msg": "Email Updated Succesfully"},status=status.HTTP_200_OK)
                return Response({"msg": "Invalid Otp..."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg":"something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
class UserProfileView(APIView):
    @swagger_auto_schema(
        operation_description="View for profile updation",
        tags=['ProfileUpdation'],
        responses={
            200:UserProfileListSerializer,
            400:"bad request",
            500:"errors"
        })
    def get(self, request):
        user = UserProfile.objects.filter(user_id=request.user.id).select_related(
            "user"
        )[0]
        serializer = UserProfileListSerializer(user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
    
    @swagger_auto_schema(
        operation_description="Update the profile section , Email and Phone Cant update from here",
        tags=['ProfileUpdation'],
        request_body=UserProfileListSerializer,
        responses={
            200:UserProfileListSerializer,
            400:"bad request",
            500:"errors"
        })
    def put(self, request):
        queryset = UserProfile.objects.get(user_id=request.user.id)
        serializer = UserProfileListSerializer(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        queryset = MyUser.objects.get(id=request.user.id)
        queryset.delete()
        return Response({"msg": "user deleted ..."}, status=status.HTTP_200_OK)


# Updating Mobile Number
@permission_classes([IsAuthenticated])
class MobilePhoneUpdate(APIView):
    @swagger_auto_schema(
        operation_description="Phone Updation View",
        tags=['ProfileUpdation'],
        responses={
            200:UserProfilePhoneSerializer,
            400:"bad request",
            500:"errors"
        })
    def get(self, request):
        if request.user.userprofile.phone:
            return Response({"phone": request.user.userprofile.phone[3:]}, status=status.HTTP_200_OK)
        return Response({"msg":"Update your phone"}, status=status.HTTP_200_OK)
        
        
           
        
    @swagger_auto_schema(
        operation_description="Update Phone here",
        tags=['ProfileUpdation'],
        request_body=UserProfilePhoneSerializer,
        responses={
            200:UserProfilePhoneSerializer,
            400:"bad request",
            500:"errors"
        }
    )
    def post(self, request):
        serializer = UserProfilePhoneSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get("phone")

            verification_sid = send_sms(phone)
            if verification_sid is not None:
                cache.set(f"{CACHE_PREFIX_MOBILE_UPDATION}_{phone}",verification_sid,30)
                return Response({"msg": "we send a otp verification number to the phone number.c0nfirm that"}, status=status.HTTP_200_OK)
            return Response(
                {"msg": "Cant send otp!!!"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# OTPVerification
@permission_classes([IsAuthenticated])
class OtpVerification(APIView):
         
    @swagger_auto_schema(
        operation_description="Enter otp in the phone here, Only input the the verification_sid and the otp",
        tags=['ProfileUpdation'],
        request_body=OtpSerilizers,
        responses={
            200:OtpSerilizers,
            400:"bad request",
            500:"errors"
        }
    )
    def post(self, request):
        phone = request.data.get('phone')
        verification_sid = cache.get(f"{CACHE_PREFIX_MOBILE_UPDATION}_{phone}")
        if verification_sid is not None:     
            otp_enterd = request.data.get("otp_enterd")
            print(otp_enterd)
            serializer = OtpSerilizers(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                verification_check = verify_user_code(verification_sid, otp_enterd)
            except:
                return Response({"msg": "Something Went Wrong..."})
            if verification_check.status == "approved":
                user = request.user.userprofile
                user.phone = verification_check.to
                user.save()

                response_data = {
                    "msg": "Success",
                }
                return Response(response_data)
            return Response(
                {"msg": "Something Went Wrong..."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {"msg": "Something Went Wrong..."},
            status=status.HTTP_400_BAD_REQUEST,
        )

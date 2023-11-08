from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import status
from ipware import get_client_ip
from django.contrib.gis.geos import Point
from authentications.modules.smtp import send_email
import urllib, json
from django.conf import settings
from threading import Thread
from authentications.modules.utils import send_sms, verify_user_code  # twilio
import random, math
from django.db.models import Q
from rest_framework.permissions import (
    IsAuthenticated,
)
from .models import (
    MyUser,
    UserProfile,
    Location,
)
from .serializers import (
    UserProfilePhoneSerializer,
    UserEmailSerializer,
    MyTokenSerializer,
    UserProfileViewSerializer,
    GoogleSocialAuthSerializer,
)


# JWTToken
def get_tokens_for_user(user, *args):
    token = MyTokenSerializer.get_token(user, *args)

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
    def get(self, request):
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
        ip_address = "157.46.156.31"  # for checking
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
        return Response(data['county'], status=status.HTTP_200_OK)


class EmailAuthAndUpdationView(APIView):
    def get(self,request):
        if request.user.is_authenticated :
            return Response({'email':request.user.email},status=status.HTTP_200_OK)
        return Response({'msg':'error'},status=status.HTTP_400_BAD_REQUEST)
        
        
    def post(self, request):
        email = request.data.get("email")
        if request.user.is_authenticated :
            if request.data.get('email') == request.user.email:
                return Response({'msg':"No Changes"},status=status.HTTP_400_BAD_REQUEST)
            else:
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
        return Response(response_data, status=status.HTTP_200_OK)


class EmailVerification(APIView):
    def post(self, request): 
        otp = request.data.get("otp")
        email = request.data.get("email")
        otp_entered = request.data.get("otp_entered")
        if int(otp) == int(otp_entered):
            if not request.user.is_authenticated:
                user = MyUser.objects.get_or_create(email=email)
                token = get_tokens_for_user(user[0])
                return Response({"token": token}, status=status.HTTP_200_OK)
            else:
                user = request.user
                user.email = email
                user.save() 
                return Response({'msg':"Email Updated Succesfully"})                
        return Response({"msg": "Invalid Otp..."}, status=status.HTTP_400_BAD_REQUEST)
    
    
               
        

@permission_classes([IsAuthenticated])
class UserProfileView(APIView):
    def get(self, request):
        user = UserProfile.objects.filter(user_id=request.user.id).select_related("user")[0]
        serializer = UserProfileViewSerializer(user)
        response_data = {
            "user": serializer.data["user"],
            "userprofile": serializer.data,
            "phone":serializer.data['phone']
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request):
        user = UserProfile.objects.get(user_id=request.user.id)
        serializer = UserProfileViewSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = MyUser.objects.get(id=request.user.id)
        user.delete()
        return Response({"msg": "user deleted ..."}, status=status.HTTP_200_OK)




# Updating Mobile Number
@permission_classes([IsAuthenticated])
class MobilePhoneUpdate(APIView):
    
    def get(self,request):
        return Response({'phone':request.user.userprofile.phone[3:]},status=status.HTTP_200_OK)
    
    def post(self, request):
        print(request.data,'kokona')
        serializer = UserProfilePhoneSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer.data,'kkona')
            phone = serializer.validated_data.get('phone')
            
            verification_sid = send_sms(phone)
            print(verification_sid,'kona')
            if verification_sid is not None:
                return Response({"sid": verification_sid}, status=status.HTTP_200_OK)
            return Response({"msg": "Cant send otp!!!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# OTPVerification
@permission_classes([IsAuthenticated])
class OtpVerification(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        verification_sid = request.data.get("verification_sid")
        try:
            verification_check = verify_user_code(verification_sid, otp)
        except:
            return Response({"msg": "Something Went Wrong..."})
        if verification_check.status == "approved":
            user = request.user.userprofile
            user.phone = verification_check.to
            user.save()
            
            response_data = {"msg": "Success", }
            return Response(response_data)
        return Response(
            {"msg": "Something Went Wrong..."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

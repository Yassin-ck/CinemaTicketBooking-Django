
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import (
    IsAuthenticated,
    )
from rest_framework import status
from ipware import get_client_ip
from django.contrib.gis.geos import Point
from authentications.modules.smtp import send_email
import urllib,json
from django.conf import settings
import random,math
#twilio
from authentications.modules.utils import send_sms,verify_user_code 
from .models import (
    MyUser,
    UserProfile,
    Location,
    )   
from .serializers import (
    PhoneSerilaizer,
    OtpSerializer,
    MyTokenSerializer,
    UserProfileViewSerializer,
    GoogleSocialAuthSerializer,
    EmailAuthViewSerializer,
    )



#JWTToken
def get_tokens_for_user(user):

    token = MyTokenSerializer.get_token(user)

    return {
        'refresh': str(token),
        'access': str(token.access_token),
    }


class GoogleSocialAuthView(APIView):
    
    def post(self,request):
        serializer = GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data,status=status.HTTP_200_OK)
            

        

class CurrentLocation(APIView):
    def get(self,request):
        client_ip,is_routable = get_client_ip(request)
        if client_ip is None:
            client_ip = "0.0.0.0"
        else:
            if is_routable:
                ip_type = "public"
            else:
                ip_type = "private"
        print(ip_type,client_ip)
        auth = settings.IP_AUTH
        ip_address = "157.46.156.31"    # for checking
        url = f"https://api.ipfind.com/?auth={auth}&ip={ip_address}"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        data['client_ip'] = client_ip
        data['ip_type'] = ip_type
        point = Point(data['longitude'],data['latitude'])
        if not Location.objects.filter(coordinates=point).exists():
           Location.objects.create(
               country = data['country'],
               state = data['region'],
               district = data['county'],
               place = data['city'],
               coordinates = point             
           ) 
        return Response(data,status=status.HTTP_200_OK)
 




class EmailAuthView(APIView):
    def post(self,request):
        serializer = EmailAuthViewSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            otp = math.floor((random.randint(100000,999999)))
            subject = 'Otp for account verification'
            message = f'Your otp for account verification {otp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_email(subject, message, email_from, recipient_list)
            request.session['email'] = email
            request.session['otp'] = otp
            return Response({"email":email},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            
            

class EmailVerification(APIView):
    def post(self,request):
        serializer = OtpSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            email = request.session.get('email')
            otp_ = request.session.get('otp')
            if otp == otp_:
                user = MyUser.objects.get_or_create(email=email)
                token = get_tokens_for_user(user[0])
                return Response({"token":token},status=status.HTTP_200_OK)
            return Response({"msg":"Invalid Otp..."})
            
            

@permission_classes([IsAuthenticated])
class UserProfileView(APIView):
    def get(self,request):
        
        print(request.user)
        user = UserProfile.objects.get(user_id=request.user.id)
        serializer = UserProfileViewSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
    def patch(self,request):
        user = UserProfile.objects.get(user_id=request.user.id)
        serializer = UserProfileViewSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self,request):
        user = MyUser.objects.get(id=request.user.id)
        user.delete()
        return Response({'msg':'user deleted ...'},status=status.HTTP_200_OK)
        



#Updating Mobile Number 
@permission_classes([IsAuthenticated])
class MobilePhoneUpdate(APIView):
    def post(self,request):
        serializer =  PhoneSerilaizer(data=request.data)
        if serializer.is_valid(): 
            phone = serializer.validated_data.get('phone')
            try:
                verification_sid = send_sms(phone)
                request.session['verification_sid'] = verification_sid
                return Response({"sid":verification_sid},status=status.HTTP_201_CREATED)

            except Exception as e:
                print(e)
            return Response({'msg': 'Cant send otp!!!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

#OTPVerification
@permission_classes([IsAuthenticated])
class OtpVerification(APIView):
    def post(self, request):
        serializer = OtpSerializer(data=request.data)  
        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            verification_sid = request.session.get('verification_sid')
            try:
                verification_check = verify_user_code(verification_sid, otp)
            except:
                return Response({'msg':'Something Went Wrong...'})
            if verification_check.status == 'approved':            
                    response_data = {
                        "msg":"Success",
                    }                                               
                    return Response(response_data)
            return Response({'msg': 'Something Went Wrong...'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors)



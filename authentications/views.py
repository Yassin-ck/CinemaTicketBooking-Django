
# from dj_rest_auth.registration.views import SocialLoginView
# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from dj_rest_auth.views import LoginView
# from rest_framework.response import Response

# class GoogleLogin(SocialLoginView):
    
#     adapter_class = GoogleOAuth2Adapter
#     callback_url = "http://localhost:8000/"
#     client_class = OAuth2Client


from .models import MyUser
from rest_framework.views import APIView
from .serializer import OtpSerilaizer,OtpSerializers,MyTokenSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
# twilio
from authentications.modules.utils import send_sms,verify_user_code
 


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    access_token = MyTokenSerializer.get_token(user)

    return {
        'refresh': str(refresh),
        'access': str(access_token),
    }


    

class OtpLogin(APIView):
    def post(self,request):
        serializer =  OtpSerilaizer(data = request.data)
        if serializer.is_valid(): 
            phone = serializer.validated_data.get('phone')
            try:
                verification_sid = send_sms(phone)
                print(verification_sid)
                request.session['otp'] = verification_sid
                request.session['phone'] = phone
                MyUser.objects.create_user(phone=phone)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(e)
            return Response({'msg': 'Cant send otp'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OtpVerification(APIView):
    def post(self, request):
        otp = request.session.get('otp')
        phone = request.session.get('phone')
        verification_sid = otp
        serializer = OtpSerializers(data=request.data)  
        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            try:
                verification_status = verify_user_code(verification_sid, otp)
            except:
                return Response({'msg':'Something Went Wrong...'})
            if verification_status == 'approved':  
                user = authenticate(phone=phone)  
                if user is not None:           
                    token = get_tokens_for_user(user)
                    response_data = {
                        "msg":"Success",
                        "token":token                       
                    }                                               
                    return Response(response_data)
            return Response({'msg': 'kona'})
        return Response(serializer.errors)
  
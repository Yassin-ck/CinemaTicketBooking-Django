from django.shortcuts import render
from rest_framework.views import APIView
from authentications.modules.utils import send_sms,verify_user_code
from rest_framework.response import Response
from rest_framework import status
from authentications.modules.smtp import send_email
from django.conf import settings
from authentications.serializers import OtpSerializer
from authentications import views
from django.db.models import Q
import random,math
from authentications.models import (
    MyUser,
    )
from .serializers import (
    TheatreRegistrationSerializer,
    TheatreLoginSerializer,
)
from .models import (
    TheareOwnerDetails,
)



# Create your views here.
class TheatreRegistration(APIView):
    def post(self,request):
        serializer = TheatreRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):   
            user = TheareOwnerDetails.objects.create(
                user = request.user,
                first_name = serializer.validated_data.get('first_name'),
                last_name = serializer.validated_data.get('last_name'),
                email = serializer.validated_data.get('email'),
                phone = serializer.validated_data.get('phone'),
                id_proof = serializer.validated_data.get('id_proof'),
                )       
            verification_sid = send_sms(user.phone)
            request.session['verification_sid'] = verification_sid
            return Response({'msg':'Otp Sent Succesfully'},status=status.HTTP_200_OK)
        return Response({'msg':'Wrong',"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)





class TheatreVerification(APIView):
    def post(self,request):
        serializer = OtpSerializer(data=request.data)
        verification_sid = request.session.get('verification_sid')
        if serializer.is_valid(raise_exception=True):
            otp_entered = serializer._validated_data.get('otp')
            verify_status = verify_user_code(verification_sid,otp_entered)
            print(verify_status.status)
            if verify_status is not None and verify_status.status == 'approved':
                try:
                    user = TheareOwnerDetails.objects.get(user=request.user)
                    subject = 'New Theatre Request'
                    message = 'New theatre is requested.. check it out !!!'
                    email_from = user.email
                    recipient_list = [settings.EMAIL_HOST_USER]
                    send_email(subject,message,email_from,recipient_list)
                    return Response({'msg':'Success'},status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'msg':f"{e}"},status=status.HTTP_400_BAD_REQUEST)                    
            return Response({'msg':'error'},status=status.HTTP_400_BAD_REQUEST)
        return Response({'error':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        
        
    

       
class TheatreLoginRequest(APIView):
    def post(self,request):
        serializer = TheatreLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            try:
                otp = math.floor(random.randint(100000,999999))
                request.session['otp'] = otp
                request.session['email'] = email
                subject = 'Otp Verification'
                message = f'Your Otp for login : {otp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_email(subject,message,email_from,recipient_list)
                return Response({'msg':'Check Email......'},status=status.HTTP_200_OK)
            except:
                return Response({"msg":"Something Went Wrong..."},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    


class TheatreLoginVerify(APIView):
    def post(self,request):
        serializer = OtpSerializer(data=request.data)
        if serializer.is_valid():
            otp = request.session.get('otp')
            otp_enterd = serializer.validated_data.get('otp')
            if otp == otp_enterd:
                email = request.session.get('email')
                try:
                    user = MyUser.objects.get(Q(theatreowner__email=email) & Q(theatreowner__is_verified=True))
                    print(user)
                except MyUser.DoesNotExist:
                    return Response({'msgt':"wait for the verification"})
                token = views.get_tokens_for_user(user)
                return Response({"msg":token},status=status.HTTP_200_OK)
            return Response({'msg':"invalid otp.."},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
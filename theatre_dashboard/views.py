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
from rest_framework.decorators import permission_classes
from .theatre_auth import TheatreAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from authentications.models import (
    MyUser,
    )
from .serializers import (
    TheatreRegistrationSerializer,
    TheatreLoginSerializer,
    RequestedLocationSerializer,
    LocationSerializer,
    TheatrOwnerFormSerializer
)
from authentications.models import (
    RequestLocation,
)
from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    Location
)



# Create your views here.


@permission_classes([IsAuthenticated])
class TheatreOwnerFormApplication(APIView):
    def post(self,request):
        serializer = TheatrOwnerFormSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):   
            user = TheareOwnerDetails.objects.create(
                user = request.user,
                first_name = serializer.validated_data.get('first_name'),
                last_name = serializer.validated_data.get('last_name'),
                email = serializer.validated_data.get('email'),
                phone = serializer.validated_data.get('phone'),
                alternative_contact = serializer.validated_data.get('alternative_contact'),
                id_proof = serializer.validated_data.get('id_proof'),
                id_number = serializer.validated_data.get('id_number'),
                address = serializer.validated_data.get('address'),
                )       
            verification_sid = send_sms(user.phone)
            request.session['verification_sid'] = verification_sid
            return Response({'msg':'Otp Sent Succesfully'},status=status.HTTP_200_OK)
        return Response({'msg':'Wrong',"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)





@permission_classes([IsAuthenticated])
class TheatreOwnerVerification(APIView):
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
                    user.is_verified = True
                    user.save()
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
        
        



@permission_classes([IsAuthenticated])
class TheatreRegistration(APIView):
    
    def post(self,request):
        serializer = TheatreRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            theatre = TheatreDetails.objects.create(
                owner = TheareOwnerDetails.objects.get(Q(user=request.user) & Q(is_approved=True)),
                theatre_name = serializer.validated_data.get('theatre_name'),
                email = serializer.validated_data.get('email'),
                phone = serializer.validated_data.get('phone'),
                alternative_contact = serializer.validated_data.get('alternative_contact'),
                location = serializer.validated_data.get('location'),
                num_of_screens = serializer.validated_data.get('num_of_screens'),
                certification = serializer.validated_data.get('certification'),
            )
            subject = "New theatre request...."
            message = 'new theatre request. check it out...'
            email_from = theatre.email
            recipient_list = [settings.EMAIL_HOST_USER]
            send_email(subject,message,email_from,recipient_list)
            return Response({'msg':'success'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



       
@permission_classes([IsAuthenticated])
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
    
    



@permission_classes([IsAuthenticated])
class TheatreLoginVerify(APIView):
    def post(self,request):
        serializer = OtpSerializer(data=request.data)
        if serializer.is_valid():
            otp = request.session.get('otp')
            otp_enterd = serializer.validated_data.get('otp')
            if otp == otp_enterd:
                email = request.session.get('email')
                try:
                    theatre = TheatreDetails.objects.get(Q(email=email) & Q(is_verified=True))
                    token = views.get_tokens_for_user(theatre.owner.user,email)
                    return Response({"msg":'loginned','token':token},status=status.HTTP_200_OK)
                except MyUser.DoesNotExist:
                    return Response({'msgt':"You are not Verified.."})
            return Response({'msg':"invalid otp.."},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    

@permission_classes([IsAuthenticatedOrReadOnly])
class SearchLocaition(APIView):
    
    def get(self,request):
        q = request.GET.get('q')
        Q_base = Q(country__icontains=q) | Q(state__icontains=q) | Q(district__icontains=q) | Q(place__icontains=q)
        location_data = Location.objects.filter(Q_base)
        if location_data:
            serializer = LocationSerializer(location_data,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"msg":"Location not found..."}, status=status.HTTP_404_NOT_FOUND)

    
    def post(self,request):
        serializer = RequestedLocationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                RequestLocation.objects.create(
                    user = request.user,
                    country = serializer.validated_data.get('country'),
                    state = serializer.validated_data.get('state'),
                    district = serializer.validated_data.get('district'),
                    place = serializer.validated_data.get('place')
                )
                subject = "New Location Requested"
                message = "New location request, check it out ......."
                email_from = request.user.email
                recipient_list = [settings.EMAIL_HOST_USER]
                send_email(subject,message,email_from,recipient_list)  
                 
            except:
                return Response({"msg":"Something went wrong`"})            
            return Response({"msg":"Your location will be updated soon..."},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

       
       
@authentication_classes([TheatreAuthentication])
class TheatreDetailsView(APIView):
    def get(self,request):
        if TheareOwnerDetails.objects.filter(user=request.user).exists():
            theatre = TheatreDetails.objects.filter(owner__user=request.user)
            serializer = TheatreRegistrationSerializer(theatre,many=True)
            return Response({'theatre':serializer.data})
            
            
            
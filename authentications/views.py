
from .models import MyUser,UserProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from authentications.modules.utils import send_sms,verify_user_code   #twilio
from .serializers import (
    PhoneSerilaizer,
    OtpSerializer,
    MyTokenSerializer,
    UserProfileViewSerializer,
    GoogleSocialAuthSerializer,
    )
 

#Registering or Login Using Phone
class PhoneLogin(APIView):
    def post(self,request):
        serializer =  PhoneSerilaizer(data=request.data)
        if serializer.is_valid(): 
            phone = serializer.validated_data.get('phone')
            try:
                verification_sid = send_sms(phone)
                request.session['otp'] = verification_sid
                request.session['phone'] = phone
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(e)
            return Response({'msg': 'Cant send otp!!!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#JWTToken
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    token = MyTokenSerializer.get_token(user)

    return {
        'refresh': str(token),
        'access': str(token.access_token),
    }


#OTPVerification
class OtpVerification(APIView):
    def post(self, request):
        otp = request.session.get('otp')
        phone = request.session.get('phone')
        verification_sid = otp
        serializer = OtpSerializer(data=request.data)  
        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            try:
                verification_status = verify_user_code(verification_sid, otp)
            except:
                return Response({'msg':'Something Went Wrong...'})
            if verification_status == 'approved':  
                user = MyUser.objects.get_or_create(phone=phone)
                if user is not None:           
                    token = get_tokens_for_user(user[0])
                    print(token)
                    response_data = {
                        "msg":"Success",
                        "token":token                       
                    }                                               
                    return Response(response_data)
            return Response({'msg': 'Something Went Wrong...'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors)





class GoogleSocialAuthView(APIView):
    
    def post(self,request):
        serializer = GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data,status=status.HTTP_200_OK)
            




















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
        return Response(serializer.errors,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def delete(self,request):
        user = MyUser.objects.get(id=request.user.id)
        user.delete()
        return Response({'msg':'user deleted ...'},status=status.HTTP_200_OK)
        


    

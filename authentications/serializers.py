from rest_framework import serializers
from .models import MyUser,UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .modules import google
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from authentications.modules.register import register_social_user

class PhoneSerilaizer(serializers.Serializer):
    phone = serializers.CharField()


class OtpSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    


class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if user.phone:
            token['phone'] = user.phone
        if user.username:
            token['username'] = user.username
        if user.email:
            token['email'] = user.email           
        
        return token
    
  
 
class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()
    
    
    def validate_auth_token(self,auth_token):
        user_data = google.Google.validate(auth_token)
        print(user_data,'lkkkk')
        try:
            user_data['sub']
            print(user_data)
        except:
            raise serializers.ValidationError(
                'The token is expired or invalid. Please login again.'
            )
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed('oops, who are you?')

        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        provider = 'google'
        
        return register_social_user(
            provider=provider,user_id=user_id,email=email,name=name,
        )
  
  
  
  
  
  
  
    
        
class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id','username','email','phone')


class UserProfileViewSerializer(GeoFeatureModelSerializer):
    user = MyUserSerializer()
    class Meta:
        model = UserProfile
        geo_field = 'location'
        fields = ('user_id','first_name','last_name','address','user')
        
        
    def update(self,instance,validated_data):
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.address = validated_data.get('address',instance.address)
        if instance.user:
            
            validated_user_data = validated_data.get('user',instance.user)
            instance.user.username = validated_user_data.get('username',instance.user.username)
            instance.user.email = validated_user_data.get('email',instance.user.email)
            instance.user.phone = validated_user_data.get('phone',instance.user.phone)
        return instance
        
    
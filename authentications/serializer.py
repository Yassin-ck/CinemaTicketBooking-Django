from rest_framework import serializers
from .models import MyUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class OtpSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('phone',)

class OtpSerializers(serializers.Serializer):
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
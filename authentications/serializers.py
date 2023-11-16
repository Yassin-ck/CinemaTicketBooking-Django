from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .modules import google
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from authentications.modules.register import register_social_user
from .models import (
    MyUser,
    UserProfile,
)


class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user, *args):
        token = super().get_token(user)
        if user.userprofile.phone:
            token["phone"] = user.userprofile.phone
        if user.username:
            token["username"] = user.username
        if user.email:
            token["email"] = user.email
        if args:
            token["theatre_email"] = args[0]
        return token


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        print(user_data, "lkkkk")
        try:
            user_data["sub"]
            print(user_data)
        except:
            raise serializers.ValidationError(
                "The token is expired or invalid. Please login again."
            )
        if user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("oops, who are you?")

        user_id = user_data["sub"]
        email = user_data["email"]
        name = user_data["name"]

        return register_social_user(
            user_id=user_id,
            email=email,
            name=name,
        )


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ("id", "username", "email")


class UserDetailsSerilaizer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class UserProfileViewSerializer(serializers.ModelSerializer):
    user = UserDetailsSerilaizer()

    class Meta:
        model = UserProfile
        fields = ("user_id", "first_name", "last_name", "address", "phone", "user")

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.address = validated_data.get("address", instance.address)

        validated_user_data = validated_data.pop("user", None)
        print(validated_user_data)
        if validated_user_data:
            instance.user.username = validated_user_data.get(
                "username", instance.user.username
            )
            instance.user.save()
        instance.save()
        return instance


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ("email",)


class UserProfilePhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("phone",)

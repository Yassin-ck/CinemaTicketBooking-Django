from rest_framework import serializers
from authentications.serializers import MyUserSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from authentications.models import (
    UserProfile,
    RequestLocation,
)
from theatre_dashboard.models import (
    TheareOwnerDetails,
    TheatreDetails,
)


class UserProfileViewSerializer(GeoFeatureModelSerializer):
    user = MyUserSerializer()

    class Meta:
        model = UserProfile
        geo_field = "location"
        fields = ("user_id", "first_name", "last_name", "user", "phone")


class RequestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLocation
        fields = "__all__"

    def update(instance, validated_data):
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        return instance


class TheatreOwnerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheareOwnerDetails
        fields = ("id", "first_name", "email", "phone", "id_number")


class TheatreOwnerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheareOwnerDetails
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "id_proof",
            "id_number",
            "address",
            "is_approved",
        )

    def update(self, instance, validated_data):
        instance.is_approved = validated_data.get("is_approved", instance.is_approved)
        instance.save()
        return instance


class TheatreDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        exclude = ("owner",)

    def update(self, instance, validated_data):
        instance.is_verified = validated_data.get("is_verified", instance.is_verified)
        instance.save()
        return instance

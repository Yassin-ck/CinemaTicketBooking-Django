from rest_framework import serializers
from rest_framework.fields import empty
from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    Location,
)
from authentications.models import (
    RequestLocation,
)


class TheatrOwnerFormSerializer(serializers.ModelSerializer):
    id_proof = serializers.ImageField()

    class Meta:
        model = TheareOwnerDetails
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "id_proof",
            "alternative_contact",
            "id_number",
            "address",
        )

    def __init__(self, instance=None, data=None, **kwargs):
        print(data)
        super().__init__(instance, data, **kwargs)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = (
            "country",
            "state",
            "district",
            "place",
        )


class RequestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLocation
        exclude = ("current_location", "user")


class TheatreRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        exclude = ("owner",)

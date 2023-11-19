from rest_framework import serializers
from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    Location,
    ScreenDetails,
    ScreenSeatArrangement,
)
from authentications.models import (
    RequestLocation,
)


class TheatrOwnerFormSerializer(serializers.ModelSerializer):
    id_proof = serializers.ImageField(required=False)

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




class ScreenDetailsSerailizer(serializers.ModelSerializer):
    
    class Meta:
        model = ScreenDetails
        fields = (
            "id",
            "theatre",
            "screen_number",
            "number_of_seats",
            "row_count",
            "column_count",
        )

    def update(self, instance, validated_data):
        instance.screen_number = validated_data.get(
            "screen_number", instance.screen_number
        )
        instance.number_of_seats = validated_data.get(
            "number_of_seats", instance.number_of_seats
        )
        instance.row_count = validated_data.get("row_count", instance.row_count)
        instance.column_count = validated_data.get(
            "column_count", instance.column_count
        )
        instance.save()
        return instance








class TheatreRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        fields = (
            "theatre_name",
            "email",
            "phone",
            "alternative_contact",
            "location",
            "num_of_screens",
            "certification",
            "address",
        )


class ScreenDetailSeatArrangementSerailizer(serializers.ModelSerializer):
    class Meta:
        model = ScreenSeatArrangement
        fields = ("seating",)


# class ScreenMovieUpdatingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ScreenDetails
#         fields = ("movies", "screen_number")

#     def update(self, instance, validated_data):
#         instance.movies = validated_data.get("movies", instance.movies)
#         instance.save()
#         return instance

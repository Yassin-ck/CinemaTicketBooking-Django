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

from .models import MoviesDetails, Languages


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
    id_proof = serializers.ImageField()

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


class TheatreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        fields = ("id", "theatre_name", "address")


class TheatreDetailsSerializer(serializers.ModelSerializer):
    owner = TheatreOwnerDetailsSerializer()

    class Meta:
        model = TheatreDetails
        fields = (
            "id",
            "theatre_name",
            "email",
            "phone",
            "alternative_contact",
            "num_of_screens",
            "certification",
            "owner",
            "address",
        )

    def update(self, instance, validated_data):
        instance.is_approved = validated_data.get("is_approved", instance.is_approved)
        instance.save()
        return instance


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = ("name",)


class MovieDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesDetails
        fields = ("id", "movie_name", "poster")


class MovieDetailsSingleSerializer(serializers.ModelSerializer):
    languages = LanguageSerializer(many=True)

    class Meta:
        model = MoviesDetails
        fields = ("movie_name", "languages", "poster", "director")

    def update(self, instance, validated_data):
        instance.movie_name = validated_data.get("movie_name", instance.movie_name)
        instance.poster = validated_data.get("poster", instance.poster)
        instance.director = validated_data.get("director", instance.director)

        language_data = validated_data.get("languages", [])
        instance.languages.clear()
        for language_data_item in language_data:
            language, created = Languages.objects.get_or_create(
                name=language_data_item["name"]
            )
            instance.languages.add(language)

        instance.save()

        return instance

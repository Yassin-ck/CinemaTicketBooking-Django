from rest_framework import serializers
from rest_framework.fields import empty
from admin_dashboard.models import MoviesDetails
from theatre_dashboard.models import (
    TheatreDetails,
    ScreenDetails,
    Shows,
    ScreenSeatArrangement,
)


class MovieDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesDetails
        fields = ("poster", "movie_name", "director")


class TheatreViewByLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        fields = ("theatre_name", "address")


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesDetails
        fields = ("movie_name",)


class ShowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shows
        fields = ("time",)


class ScreenDetailsSerializer(serializers.ModelSerializer):
    movies = MovieSerializer()
    shows = ShowsSerializer(many=True)

    class Meta:
        model = ScreenDetails
        fields = ("movies", "shows")


class ScreenSeatingSerializer(serializers.ModelSerializer):
    screen = ScreenDetailsSerializer()

    class Meta:
        model = ScreenSeatArrangement
        fields = ("seating", "screen")

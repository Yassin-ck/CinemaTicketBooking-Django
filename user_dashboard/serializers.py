from rest_framework import serializers
from admin_dashboard.models import (
    MoviesDetails,
    Languages,
)
from theatre_dashboard.models import (
    TheatreDetails,
    ScreenDetails,
    Shows,
    ScreenSeatArrangement,
    ShowTime,
)


class MovieDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesDetails
        fields = ("poster", "movie_name", "director")


class TheatreViewByLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        fields = ("theatre_name", "address")


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = ('name',)


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesDetails
        fields = ("movie_name",)


class ShowTImeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTime
        fields = ("time",)


class ShowsSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()
    movies = MovieSerializer()
    show_time = ShowTImeSerializer(many=True)

    class Meta:
        model = Shows
        fields = ("show_time", "movies","language")


class ScreenDetailsSerializer(serializers.ModelSerializer):
    shows_set = ShowsSerializer(many=True)
    theatre = TheatreViewByLocationSerializer()

    class Meta:
        model = ScreenDetails
        fields = ("screen_number", "shows_set", "theatre")


class ScreenSeatingSerializer(serializers.ModelSerializer):
    screen = ScreenDetailsSerializer()

    class Meta:
        model = ScreenSeatArrangement
        fields = ("seating", "screen")

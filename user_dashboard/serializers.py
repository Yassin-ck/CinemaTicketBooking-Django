from rest_framework import serializers
from datetime import datetime,timedelta
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
    ShowDates
)


class MovieDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesDetails
        fields = ("poster", "movie_name", "director")


class TheatreViewByLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        fields = ("theatre_name", "address")

class TheatreViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        fields = ("theatre_name",)


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

class ShowDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowDates
        fields = ("dates",)

class ShowsSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()
    movies = MovieSerializer()
    show_time = ShowTImeSerializer(many=True)
    show_dates = ShowDatesSerializer(many=True)

    class Meta:
        model = Shows
        fields = ("show_time", "movies","language","show_dates")
        
        
    # def to_representation(self, instance):
    #     filtered_dates = [date for date in instance.show_dates.all() if date.dates <= datetime.today().date() +timedelta(days=3)]
    #     instance.show_dates.set(filtered_dates)  
    #     return super().to_representation(instance)
        
    

class ScreenDetailsSerializer(serializers.ModelSerializer):
    shows_set = ShowsSerializer(many=True)
    theatre = TheatreViewSerializer()

    class Meta:
        model = ScreenDetails
        fields = ("screen_number", "shows_set", "theatre")


class ScreenSeatingSerializer(serializers.ModelSerializer):
    screen = ScreenDetailsSerializer()

    class Meta:
        model = ScreenSeatArrangement
        fields = ("seating", "screen")

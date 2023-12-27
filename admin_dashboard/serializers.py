from rest_framework import serializers
from user_dashboard.serializers import RatingListSerializer
from .models import(
     MoviesDetails,
     Languages
     )


class LanguageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = ("name",)
        
class LanguageChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = ("name",)



class MovieDetailListSerializer(serializers.ModelSerializer):
    rating = RatingListSerializer(source="rating_set",many=True)
    class Meta:
        model = MoviesDetails
        fields = (
            "id",
            "movie_name",
            "poster",
            "director",
            "rating"
            )


class MovieDetailsChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesDetails
        fields = (
            "movie_name",
            )

class MovieDetailsCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MoviesDetails
        fields = (
            "movie_name",
            "poster",
            "director"
            )

    def update(self, instance, validated_data):
        instance.movie_name = validated_data.get("movie_name", instance.movie_name)
        instance.poster = validated_data.get("poster", instance.poster)
        instance.director = validated_data.get("director", instance.director)
        instance.save()
        return instance


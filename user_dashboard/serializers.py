from rest_framework import serializers
from admin_dashboard.models import MoviesDetails


class MovieDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesDetails
        fields = ('poster','movie_name','director')
        
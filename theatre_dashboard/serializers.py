from rest_framework import serializers
from django.db import transaction

from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    ScreenDetails,
    ShowDates,
    ShowTime,
    Shows,
    ScreenSeatArrangement,
)
from admin_dashboard.serializers import (
    LanguageChoiceSerializer,
    MovieDetailsChoiceSerializer
)

class TheatreOwnerListSerializer(serializers.ModelSerializer):
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

class TheatrOwnerCreateUpdateSerializer(serializers.ModelSerializer):
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

    def update(self, instance, validated_data):
        instance.is_approved = validated_data.get("is_approved", instance.is_approved)
        instance.save()
        return instance




class TheatreOwnerChoiceSerializer(serializers.ModelSerializer):
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


class TheatreDetailsCreateUpdateSerializer(serializers.ModelSerializer):

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

class TheatreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        fields = (
            "id",
            "theatre_name",
            "address",
        )
        
        
class TheatreListChoiceSerializer(serializers.ModelSerializer):
    owner = TheatreOwnerChoiceSerializer()
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

        
class ShowTimeChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTime
        fields = ("time",)
        
        
        
class ShowDatesChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowDates
        fields = ("dates",)
        



class ShowCreateUpdateSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Shows
        fields = (
            'show_time',
            'show_dates',
            'language',
            'movies',
            'screen'
            )   
        

    
    def create(self, validated_data):
        show_time = validated_data.get('show_time')
        show_dates = validated_data.get('show_dates')
        language = validated_data.get('language')
        movies = validated_data.get('movies')
        screen = validated_data.get('screen')
        try:
            instance = Shows.objects.create(
                language = language,
                movies = movies,
                screen = screen     
                )
            instance.show_dates.add(*show_dates)
            instance.show_time.add(*show_time)
            instance.save()   
        except:
            raise serializers.ValidationError({'error':"Something Went Wrong..."})
        return validated_data
        

            
    def update(self, instance, validated_data):
        show_time = validated_data.get('show_time')
        show_dates = validated_data.get('show_dates')
        with transaction.atomic():               
            if 'show_time' in validated_data :
                instance.show_time.clear()
                instance.show_time.add(*show_time)
            if 'show_dates' in validated_data:
                instance.show_dates.clear()
                instance.show_dates.add(*show_dates)
            instance.language = validated_data.get('language', instance.language)
            instance.movies = validated_data.get('movies', instance.movies)
            instance.screen = validated_data.get('screen', instance.screen)
        
            instance.save()
        return instance


class ShowsChoiceSerializer(serializers.ModelSerializer):
    language = LanguageChoiceSerializer()
    movies = MovieDetailsChoiceSerializer()
    show_time = ShowTimeChoiceSerializer(many=True)
    show_dates = ShowDatesChoiceSerializer(many=True)

    class Meta:
        model = Shows
        fields = (
            "show_time",
            "movies",
            "language",
            "show_dates"
            )
            


class ScreenDetailsListSerializer(serializers.ModelSerializer):
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
        
class ScreenDetailsCreateUpdateSerailizer(serializers.ModelSerializer):
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
        instance.screen_number = validated_data.get("screen_number", instance.screen_number)
        instance.number_of_seats = validated_data.get("number_of_seats", instance.number_of_seats)
        instance.row_count = validated_data.get("row_count", instance.row_count)
        instance.column_count = validated_data.get("column_count", instance.column_count )
        if  int(instance.column_count) * int(instance.row_count) != int(instance.number_of_seats):
            raise serializers.ValidationError({'error': 'The product of row count and column count must equal the number of seats.'})
        instance.is_approved=True
        instance.save()
        return instance


class ScreenDetailsChoicesSerializer(serializers.ModelSerializer):
    shows_set = ShowsChoiceSerializer(many=True)
    theatre = TheatreListSerializer()

    class Meta:
        model = ScreenDetails
        fields = (
            "screen_number",
            "shows_set", 
            "theatre",
            "row_count",
            "column_count"
            )
    
    
    


class ScreenSeatArrangementListSerailizer(serializers.ModelSerializer):
    class Meta:
        model = ScreenSeatArrangement
        fields = ("seating",)
        
        
class ScreenSeatArrangementCreateUpdateSerailizer(serializers.ModelSerializer):
    class Meta:
        model = ScreenSeatArrangement
        fields = ("seating",)


class ScreenSeatArrangementChoiceSerailizer(serializers.ModelSerializer):
    screen = ScreenDetailsChoicesSerializer()
    class Meta:
        model = ScreenSeatArrangement
        fields = (
            "seating",
            "screen"
            )




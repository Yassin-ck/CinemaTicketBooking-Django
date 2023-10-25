from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    ScreenDetails,
    Location,
    )
from authentications.models import (
    RequestLocation,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TheatreRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheareOwnerDetails
        fields = ('first_name','last_name','email','phone','id_proof')
        

class TheatreLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    
    
class TheatreDetailsFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        fields = ('theatre_name','location','num_of_screens','certification')
        
        
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('country','state','district','place')
        
     
class RequestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLocation
        exclude = ('current_location','user')
        
    
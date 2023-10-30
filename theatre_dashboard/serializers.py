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


class TheatrOwnerFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheareOwnerDetails
        fields = ('first_name','last_name','email','phone','id_proof','alternative_contact','id_number','address')
        

    
        
        
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = (
            'country',
            'state',
            'district',
            'place',
            )
        
     
class RequestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLocation
        exclude = ('current_location','user')
        

class TheatreRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreDetails
        exclude = ('owner',)
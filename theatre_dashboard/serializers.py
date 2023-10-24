from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (
    TheareOwnerDetails,
    )
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TheatreRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheareOwnerDetails
        fields = ('first_name','last_name','email','phone','id_proof')
        

class TheatreLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
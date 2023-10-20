from rest_framework import serializers
from authentications.serializers import MyUserSerializer
from authentications.models import MyUser,UserProfile,RequestLocation
from rest_framework_gis.serializers import GeoFeatureModelSerializer
        
class UserProfileViewSerializer(GeoFeatureModelSerializer):
    user = MyUserSerializer()
    class Meta:
        model = UserProfile
        geo_field = 'location'
        fields = ('user_id','first_name','last_name','user','phone')
        
    


class  RequestedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLocation
        fields = "__all__"
        
        
        
    def update(instance,validated_data):
        instance.status = validated_data.get('status',instance.status)
        instance.save()
        return instance
        
    
from rest_framework import serializers
from authentications.serializers import MyUserSerializer
from authentications.models import MyUser,UserProfile
from rest_framework_gis.serializers import GeoFeatureModelSerializer
        
class UserProfileViewSerializer(GeoFeatureModelSerializer):
    user = MyUserSerializer()
    class Meta:
        model = UserProfile
        geo_field = 'location'
        fields = ('user_id','first_name','last_name','user')
        
    
    
        
    
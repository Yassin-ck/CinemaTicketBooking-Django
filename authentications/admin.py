from django.contrib import admin
from .models import MyUser,UserProfile
# Register your models here.
from django.contrib.gis.admin import OSMGeoAdmin


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id','username','phone','email')
@admin.register(UserProfile)
class UserProfiileAdmin(OSMGeoAdmin):
    list_display = ('user_id','first_name','last_name','address','location')
from django.contrib import admin
from .models import (
    MyUser,
    UserProfile,
    Location,
    RequestLocation,
)

# Register your models here.
from django.contrib.gis.admin import OSMGeoAdmin


@admin.register(MyUser)
class MyUserAdmin(OSMGeoAdmin):
    list_display = ("id", "username", "email")


@admin.register(UserProfile)
class UserProfiileAdmin(OSMGeoAdmin):
    list_display = (
        "user_id",
        "first_name",
        "last_name",
        "phone",
        "address",
    )


@admin.register(Location)
class LocationAdmin(OSMGeoAdmin):
    list_display = ("id", "coordinates", "country", "state", "district", "place")


@admin.register(RequestLocation)
class RequestedLocationAdmin(OSMGeoAdmin):
    list_display = ("place", "status", "country", "state", "district")

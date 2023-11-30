from django.contrib import admin
from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    ScreenDetails,
    ScreenSeatArrangement,
    Shows,
    ShowTime,
    ShowDates
)

# Register your models here.
admin.site.register(TheareOwnerDetails)
admin.site.register(TheatreDetails)
admin.site.register(ScreenSeatArrangement)


@admin.register(ScreenDetails)
class ScreenDetailsAdmin(admin.ModelAdmin):
    list_display = ('id',"screen_number","is_approved")


@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ("id",'time',)
    
    
    
@admin.register(ShowDates)
class ShowDatesAdmin(admin.ModelAdmin):
    list_display = ("id",'dates',)
    
    
    
@admin.register(Shows)
class ShowsAdmin(admin.ModelAdmin):
    list_display = ("id","screen",'language','movies')
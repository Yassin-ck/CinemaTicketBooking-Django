from django.contrib import admin
from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    ScreenDetails,
    ScreenSeatArrangement,
    Shows,
)

# Register your models here.
admin.site.register(TheareOwnerDetails)
admin.site.register(TheatreDetails)
admin.site.register(ScreenDetails)
admin.site.register(ScreenSeatArrangement)
admin.site.register(Shows)

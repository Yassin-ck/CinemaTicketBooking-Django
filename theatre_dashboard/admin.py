from django.contrib import admin
from .models import (
    TheareOwnerDetails,
    TheatreDetails,
    ScreenDetails,
)
# Register your models here.
admin.site.register(TheareOwnerDetails)
admin.site.register(TheatreDetails)
admin.site.register(ScreenDetails)
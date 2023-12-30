from django.contrib import admin
from .models import MoviesDetails, Languages

# Register your models here.


class MoviesDetailsAdmin(admin.ModelAdmin):
    list_display = ("id", "movie_name")


admin.site.register(MoviesDetails, MoviesDetailsAdmin)

admin.site.register(Languages)

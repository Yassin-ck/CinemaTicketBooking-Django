from django.urls import path
from .views import (
    MovieOrTheatreSearching
)
urlpatterns = [
    path('search/',MovieOrTheatreSearching.as_view(),name='moviesearching')
]
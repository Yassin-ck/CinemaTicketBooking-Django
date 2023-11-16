from django.urls import path
from .views import (
    MovieSearching,
    MovieSelectionView,
    TheatreSelectionView,
)

urlpatterns = [
    path("search/", MovieSearching.as_view(), name="moviesearching"),
    path("movieslist/", MovieSelectionView.as_view(), name="movieslist"),
    path("theatrelist/", TheatreSelectionView.as_view(), name="theatrelist"),
]

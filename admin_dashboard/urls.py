from django.urls import path
from .views import (
    UserProfileViewBYAdmin,
    )

urlpatterns = [
    path("users/", UserProfileViewBYAdmin.as_view(), name="users"),
]
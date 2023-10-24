from django.urls import path
from .views import (
    UserProfileViewBYAdmin,TheatreOwnerRequest
    
    )

urlpatterns = [
    path("users/", UserProfileViewBYAdmin.as_view(), name="users"),
    path("theatreowner/", TheatreOwnerRequest.as_view(), name="theatreowner"),
    path("theatreowner/<int:pk>/", TheatreOwnerRequest.as_view(), name="ownerdetails"),
]
from django.urls import path
from .views import (
    BookedView,
    MovieSearching,
    MovieSelectionView,
    TheatreSelectionView,
    SingleMovieDetailsView,
    TicketCachingView,
    StripeCheckoutView,
    TicketBookingApi,
    BookedView,
)

urlpatterns = [
    path("search/", MovieSearching.as_view(), name="moviesearching"),
    path("movieslist/", MovieSelectionView.as_view(), name="movieslist"),
    path("theatrelist/", TheatreSelectionView.as_view(), name="theatrelist"),
    path('moviedetailsview/<str:movie>/<int:id>/',SingleMovieDetailsView.as_view(),name='moviesdetialsview'),
    path('ticketcaching/',TicketCachingView.as_view(),name="ticketcaching"),
    path('ticketbooking/',TicketBookingApi.as_view(),name="ticketbooking"),
    path('createcheckoutsession/',StripeCheckoutView.as_view(),name='createcheckoutsession'),
    path('bookedticketview/',BookedView.as_view(),name='bookedticketview')
]

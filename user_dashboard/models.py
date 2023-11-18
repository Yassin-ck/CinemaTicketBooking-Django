from django.contrib.gis.db import models
from authentications.models import MyUser
from theatre_dashboard.models import (
    Shows,
    ScreenDetails,
)


# class Payments(models.Model):
#     pass

class TicketBooking(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    show = models.ForeignKey(Shows, on_delete=models.SET_NULL, null=True)
    tickets = models.JSONField()
    theatre_screen = models.ForeignKey(ScreenDetails, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    
    

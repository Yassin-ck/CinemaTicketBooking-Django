from django.contrib.gis.db import models
from authentications.models import MyUser
from theatre_dashboard.models import (
    Shows,
    ScreenDetails,
    )   

class TicketBooking(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,blank=True)
    show = models.ForeignKey(Shows,on_delete=models.SET_NULL,null=True)
    number_of_tickets = models.CharField(max_length=2)
    theatre_screen = models.ForeignKey(ScreenDetails,on_delete=models.CASCADE)
    

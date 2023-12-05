from django.contrib.gis.db import models
from authentications.models import MyUser
from theatre_dashboard.models import (
    Shows,
    ScreenDetails,
    ShowDates,
    ShowTime
)



class BookingDetails(models.Model):
    show = models.ForeignKey(Shows, on_delete=models.CASCADE)
    theatre_screen = models.ForeignKey(ScreenDetails, on_delete=models.CASCADE)
    
class BookingTime(models.Model):
    ticketdetails = models.ForeignKey(BookingDetails,on_delete=models.CASCADE)
    time = models.ForeignKey(ShowTime,on_delete=models.CASCADE)


class BookingDate(models.Model):
    bookingtime = models.ForeignKey(BookingTime,on_delete=models.CASCADE)  
    showdate = models.ForeignKey(ShowDates,on_delete=models.CASCADE)


class TicketBooking(models.Model):
    date = models.ForeignKey(BookingDate,on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE)
    tickets = models.JSONField()
    booking_date = models.DateTimeField(auto_now_add=True)
    

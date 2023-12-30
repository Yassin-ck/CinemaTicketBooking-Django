from django.contrib.gis.db import models
from authentications.models import MyUser
from theatre_dashboard.models import Shows, ShowDates, ShowTime
from admin_dashboard.models import MoviesDetails


class TicketBooking(models.Model):
    show = models.ForeignKey(Shows, on_delete=models.CASCADE)
    time = models.ForeignKey(ShowTime, on_delete=models.CASCADE)
    date = models.ForeignKey(ShowDates, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    tickets = models.JSONField()
    booking_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.CharField(max_length=10)
    payment_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ("show", "time", "date", "tickets")


class Rating(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(MoviesDetails, on_delete=models.CASCADE)
    star = models.CharField(max_length=5)


class Review(models.Model):
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE)
    review = models.TextField()

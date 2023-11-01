from django.contrib.gis.db import models
from authentications.models import MyUser, Location

# Create your models here.


class TheareOwnerDetails(models.Model):
    user = models.ForeignKey(
        MyUser, on_delete=models.PROTECT, related_name="theatreownerdetails"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    alternative_contact = models.CharField(
        max_length=13, unique=True, null=True, blank=True
    )
    id_number = models.CharField(max_length=100)
    id_proof = models.ImageField(upload_to="owner_id_proof/")
    address = models.TextField()
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)


class TheatreDetails(models.Model):
    owner = models.ForeignKey(
        TheareOwnerDetails, on_delete=models.PROTECT, related_name="theatreowner"
    )
    theatre_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    # movies = models.ForeignKey('MovieDetails',on_delete=models.PROTECT)
    phone = models.CharField(max_length=13, unique=True)
    alternative_contact = models.CharField(
        max_length=13, unique=True, null=True, blank=True
    )
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    num_of_screens = models.CharField(max_length=2)
    certification = models.ImageField(upload_to="TheatreCertification/")
    is_approved = models.BooleanField(default=False)


class ScreenDetails(models.Model):
    theatre = models.ForeignKey(TheatreDetails, on_delete=models.CASCADE)
    screen_number = models.IntegerField(null=True, blank=True)
    number_of_seats = models.IntegerField(null=True, blank=True)
    row_count = models.IntegerField(null=True, blank=True)
    column_count = models.IntegerField(null=True, blank=True)
    seat_arrangement = models.JSONField(null=True, blank=True)

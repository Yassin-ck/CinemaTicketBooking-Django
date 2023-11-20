from django.contrib.gis.db import models
from authentications.models import MyUser, Location
from admin_dashboard.models import  (
    MoviesDetails,
    Languages
    )

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
    id_proof = models.ImageField(upload_to="owner_id_proof/", null=True, blank=True)
    address = models.TextField()
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.username} theatre owner"


class TheatreDetails(models.Model):
    owner = models.ForeignKey(
        TheareOwnerDetails, on_delete=models.PROTECT, related_name="theatreowner"
    )
    theatre_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    alternative_contact = models.CharField(
        max_length=13, unique=True, null=True, blank=True
    )
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    address = models.TextField()
    num_of_screens = models.CharField(max_length=2)
    certification = models.ImageField(upload_to="TheatreCertification/")
    is_approved = models.BooleanField(default=False)


    def __str__(self) -> str:
        return self.theatre_name


class ShowTime(models.Model):
    time = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.time)

class ShowDates(models.Model):
    dates = models.DateField()
    
    def __str__(self) -> str:
        return f"{self.dates}"
    
    
    
class Shows(models.Model):
    show_time = models.ManyToManyField(ShowTime, blank=True,related_name="showtime")
    show_dates = models.ManyToManyField(ShowDates, blank=True,related_name='showdate')
    movies = models.ForeignKey(
        MoviesDetails, on_delete=models.PROTECT, null=True, blank=True
    )
    language = models.ForeignKey(Languages,on_delete=models.DO_NOTHING)
    screen = models.ForeignKey(
        "ScreenDetails", on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self) -> str:
        return  f"{self.id}"
    


class ScreenDetails(models.Model):
    theatre = models.ForeignKey(
        TheatreDetails, on_delete=models.CASCADE, related_name="screen_details"
    )
    screen_number = models.IntegerField(null=True, blank=True)
    number_of_seats = models.IntegerField(null=True, blank=True)
    row_count = models.IntegerField(null=True, blank=True)
    column_count = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.theatre.theatre_name}'s screen number {self.screen_number}"


class ScreenSeatArrangement(models.Model):
    screen = models.OneToOneField(
        ScreenDetails, primary_key=True, on_delete=models.CASCADE
    )
    STATUS = [
        ("NONE", "WHITE"),
        ("BOOKED", "WHITE"),
        ("BOOKING", "GREEN"),
    ]
    seating = models.JSONField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.screen.screen_number)

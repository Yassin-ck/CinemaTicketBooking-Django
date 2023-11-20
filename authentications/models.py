# Create your models here.
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.gis.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, email=None, username=None, password=None, **kwargs):
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, username=None, password=None, **kwargs):
        user = self.create_user(email=email, username=username)
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    date_joined = models.DateField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Location(models.Model):
    coordinates = models.PointField(srid=4326)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)

    @property
    def longitude(self):
        return self.coordinates.x

    @property
    def latitude(self):
        return self.coordinates.y

    def __str__(self) -> str:
        return self.place


class RequestLocation(models.Model):
    STATUS = [
        ("PENDING", "PENDING"),
        ("ACCEPTED", "ACCEPTED"),
        ("REJECTED", "REJECTED"),
    ]

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    status = models.CharField(default="PENDING", choices=STATUS, max_length=10)

    def __str__(self) -> str:
        return f"{self.user.username} location request"


class UserProfile(models.Model):
    user = models.OneToOneField(
        MyUser, on_delete=models.CASCADE, primary_key=True, related_name="userprofile"
    )
    phone = models.CharField(max_length=20, unique=True, null=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} profile"

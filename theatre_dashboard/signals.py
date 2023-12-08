from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import (
    ScreenDetails,
    TheatreDetails,
    ScreenSeatArrangement,
    Shows,
    )


@receiver(post_save, sender=TheatreDetails)
def create_screens_for_theatres(sender, instance, created, *args, **kwargs):
    if created:
        for i in range(int(instance.num_of_screens)):
            screens = ScreenDetails(theatre=instance)
            screens.save()


@receiver(post_save, sender=ScreenDetails)
def create_Seat_for_Screens(sender, instance, created, *args, **kwargs):
    if created:
        ScreenSeatArrangement.objects.create(screen=instance)





  
from django.dispatch import receiver
from django.db.models.signals import post_save
from user_dashboard.models import (
    BookingDetails,
    )
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




@receiver(post_save, sender=Shows)
def create_booking_details_instance(sender, instance, created, *args, **kwargs):
    if created:
        BookingDetails.objects.get_or_create(
            show=instance,
            theatre_screen=instance.screen
        )

  
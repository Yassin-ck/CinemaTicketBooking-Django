from django.contrib import admin
from .models import (
    TicketBooking,
    BookingDate,
    BookingDetails,
    BookingTime
    )

# Register your models here.
admin.site.register(TicketBooking)
admin.site.register(BookingDate)
admin.site.register(BookingDetails)
admin.site.register(BookingTime)

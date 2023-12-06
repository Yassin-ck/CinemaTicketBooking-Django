from django.contrib import admin
from .models import (
    TicketBooking,
    BookingDetails,
    )

# Register your models here.
admin.site.register(TicketBooking)
admin.site.register(BookingDetails)

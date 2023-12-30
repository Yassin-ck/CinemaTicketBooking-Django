from django.contrib import admin
from .models import TicketBooking, Review, Rating

# Register your models here.
admin.site.register(TicketBooking)
admin.site.register(Review)
admin.site.register(Rating)

from rest_framework import serializers
from .models import (
    BookingDetails,
    TicketBooking
    )

class TicketBookingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketBooking
        fields = (
            "date",
            "tickets",
            "time",
        )
        
    def create(self, validated_data):
        print(self.context['request'].data,'kkk')
        date = validated_data.get("date")
        tickets = validated_data.get("tickets")
        time = validated_data.get("time")
        user = self.context['request'].user
        
        print(date,tickets,time,user)
        return super().create(validated_data)
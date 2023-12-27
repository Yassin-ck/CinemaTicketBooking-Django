from rest_framework import serializers

from .models import (
    TicketBooking,
    Rating,
    Review
    )
from authentications.serializers import UserDetailsChoiceSerilaizer

class TicketBookingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketBooking
        fields = (
            "date",
            "tickets",
            "time",
            "show",
            "user",
            "payment_id",
            "amount_paid"
        )
        
   
    def create(self, validated_data):       
        date = validated_data.get('date')
        time = validated_data.get('time')
        show = validated_data.get('show')
        tickets = validated_data.get('tickets')
        user = validated_data.get('user')
        payment_id = validated_data.get('payment_id')
        amount_paid = validated_data.get('amount_paid')
        ticket_booking = TicketBooking.objects.create(
            show=show,
            time=time,
            date=date,
            user=user,
            tickets=tickets,
            payment_id=payment_id,
            amount_paid=amount_paid
        )

        return ticket_booking
    
class ReviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('review',)
    
class RatingListSerializer(serializers.ModelSerializer):
    review = ReviewListSerializer()
    user = UserDetailsChoiceSerilaizer()
    
    class Meta:
        model = Rating
        fields = ('id','star','review','user')


class RatingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('user','movie','star')
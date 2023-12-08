from django.forms import ValidationError
from rest_framework import serializers
from django.db.models import Q

from utils.mapping_variables import Available_dates
from .models import (
    TicketBooking
    )
from theatre_dashboard.models import (
    ShowDates,
    Shows
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
        request_data = self.context['request'].data
        date_str = str(validated_data.get("date"))
        tickets = validated_data.get("tickets")
        time = validated_data.get("time")
        user = self.context['request'].user

        if date_str not in Available_dates:
            raise serializers.ValidationError("You can't book on this date")

        try:
            show_data = Shows.objects.get(
                Q(screen__screen_number=request_data['screen_number']) &
                Q(screen__theatre__theatre_name=request_data['theatre_name']) &
                Q(show_dates__dates=date_str) &
                Q(show_time__time=time)
            )
            
            date_instance = ShowDates.objects.get(dates=date_str)
            validated_data.update({
                'date': date_instance,
                'tickets': tickets,
                'time': time,
                'show': show_data,
            })
            if user.is_authenticated:
               validated_data['user'] = user


            return super().create(validated_data)

        except Shows.DoesNotExist:
            raise serializers.ValidationError("Show not found for the specified details")

        except ShowDates.DoesNotExist:
            raise serializers.ValidationError("Date not found in available dates")

        except Exception as e:
            raise serializers.ValidationError(f"Something went wrong: {e}")
        

from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework import status

def send_email(subject, message, sender, recipient_list):
    email = EmailMessage(subject, message, sender, recipient_list)
    email.send()



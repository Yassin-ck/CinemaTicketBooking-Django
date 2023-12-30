from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from authentications.models import MyUser


@shared_task(bind=True)
def send_mail_func(self):
    users = MyUser.objects.all()
    for user in users:
        mail_subject = "hello celery"
        message = "New Movie Added"
        to_email = user.email
        send_mail(
            subject=mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=True,
        )
    return "Task Successfull"

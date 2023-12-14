from twilio.rest import Client
from django.conf import settings
from twilio.base.exceptions import TwilioRestException

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)


def send_sms(phone_number):
    try:
        verification = client.verify.v2.services(
            settings.SERVICE_SID
        ).verifications.create(to=phone_number, channel="sms")
        print(verification.sid, "lllll")
        return verification.sid
    except Exception as e:
        print(e)
        return


def verify_user_code(verification_sid, user_input):
    try:
        verification_check = client.verify.v2.services(
            settings.SERVICE_SID
        ).verification_checks.create(verification_sid=verification_sid, code=user_input)
        return verification_check
    except Exception as e:
        print(e)
        return


def send_whatsapp_message(number):
    media_url = 'https://imgs.search.brave.com/OuC1MTdFjW3aBb6A9sFZFYUxelELr43SMPyYSyCwVU8/rs:fit:860:0:0/g:ce/aHR0cHM6Ly9sb2dv/bWFrZXJyLmFpL2Js/b2cvd3AtY29udGVu/dC91cGxvYWRzLzIw/MjIvMDUvaWtlYS1s/b2dvLTEtMTAyNHg2/MTQucG5n'
    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    message = client.messages.create(
                                from_='whatsapp:+14155238886',
                                body='Hello, there!',
                                to=f'whatsapp:{number}',
                                media_url=[media_url]
                            )

    print(message.sid)
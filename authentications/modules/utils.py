from twilio.rest import Client
from django.conf import settings
from twilio.base.exceptions import TwilioRestException

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

client = Client(settings.ACCOUNT_SID,settings.AUTH_TOKEN)
def send_sms(phone_number):
    print(phone_number)
    try: 
        verification = client.verify \
                        .v2 \
                        .services(settings.SERVICE_SID) \
                        .verifications \
                        .create(to=phone_number, channel='sms')
        print(verification.sid,'lllll')
        return verification.sid
    except ConnectionError as e:
        print(e,'ll')
        raise e
       

def verify_user_code(verification_sid, user_input):
# Initialize the Twilio client using your account SID and auth token
    try:
        verification_check = client.verify \
        .v2 \
        .services(settings.SERVICE_SID) \
        .verification_checks\
        .create(verification_sid=verification_sid, code=user_input)
        return verification_check.status
    except TwilioRestException as e:
        raise e
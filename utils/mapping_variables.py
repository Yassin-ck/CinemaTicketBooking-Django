from datetime import datetime,timedelta

row_alpha = [
                    "A",
                    "B",
                    "C",
                    "D",
                    "E",
                    "F",
                    "G",
                    "H",
                    "I",
                    "J",
                    "K",
                    "L",
                    "M",
                    "N",
                    "O",
                    "P",
                    "Q",
                    "R",
                    "S",
                    "T",
                    "U",
                    "V",
                    "W",
                    "X",
                    "Y",
                    "Z",
                ] 



today = datetime.today().date()
to_third_day = today + timedelta(days=3)
Available_dates = (str(today),str(today+timedelta(days=1)),str(today+timedelta(days=2)),str(to_third_day))




UPCOMING = "UPCOMING"
PENDING = "PENDING"
RELEASED = "RELEASED"
 



CACHE_PREFIX_TICKET_BOOKING = "ticket_booking_api"
CACHE_TIME = 60 * 10
CACHED = "b"
BOOKED = "w"
CACHE_PREFIX_EMAIL_AUTHENTICATION = "email_authentication_cache"
CACHE_PREFIX_EMAIL_UPDATION = "email_updation_cache"
CACHE_PREFIX_MOBILE_UPDATION = "mobile_updation_cache"
CACHE_PREFIX_TICKET_DETAILS = "ticket_details_cache"
CACHE_TIME_TICKET_DETAILS = 60 * 2
CACHE_PREFIX_THEATRE_AUTH = "theatre_authentication_cache"




MOVIE = 'movie'
LANGUAGE = 'language'
DATES = 'dates'
TIME = 'time'
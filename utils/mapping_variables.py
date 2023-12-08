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

UPCOMING = "UPCOMING"
PENDING = "PENDING"
RELEASED = "RELEASED"
 
Available_dates = (str(today),str(today+timedelta(days=1)),str(today+timedelta(days=2)),str(to_third_day))
CACHE_PREFIX = "ticket_booking_api"
CACHE_TIME = 60 * 10
CACHED = "b"
BOOKED ="w"
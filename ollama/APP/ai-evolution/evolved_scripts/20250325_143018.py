# Purpose: > Get the current date and print whether it's a weekday or weekend

import datetime
from calendar import mdays

def get_weekday_or_weekend():
    today = datetime.date.today()
    if today.weekday() < 5:
        return "Weekday"
    else:
        return "Weekend"

print(get_weekday_or_weekend())
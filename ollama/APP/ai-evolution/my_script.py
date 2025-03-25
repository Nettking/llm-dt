import datetime

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def format_datetime(dt):
    return dt.strftime(DATE_FORMAT)

def get_week_number(dt):
    return dt.isocalendar()[1]

def get_days_until_april_1(dt):
    target_date = datetime.datetime(dt.year, 4, 1)
    if target_date < dt:
        target_date = datetime.datetime(target_date.year + 1, 4, 1)
    return (target_date - dt).days

current_datetime = datetime.datetime.now()
print("Current Date and Time: ", format_datetime(current_datetime))
print("Week Number: ", get_week_number(current_datetime))
print("Days until April 1: ", get_days_until_april_1(current_datetime))
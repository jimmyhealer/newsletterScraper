from datetime import datetime, timedelta
import re

def closest_weekday_before_today():
    today = datetime.today()
    delta_days = 0

    # Loop to find the most recent weekday
    while today.weekday() in [5, 6]:  # 5: Saturday, 6: Sunday
        today -= timedelta(days=1)
        delta_days += 1

    return today.strftime("%Y/%m/%d")


# Function to calculate working days between a given date and today
def working_days_between(date_str):
    date_given = datetime.strptime(date_str, "%Y/%m/%d")
    today = datetime.today()
    if date_given > today:
        start_date, end_date = today, date_given
    else:
        start_date, end_date = date_given, today

    working_days = 0

    while start_date < end_date:
        if start_date.weekday() < 5:  # Monday to Friday are working days
            working_days += 1
        start_date += timedelta(days=1)

    return working_days

def add_working_day(date_str):
    today = datetime.today()
    date = datetime.strptime(date_str, "%Y/%m/%d")

    need_dates = []

    while date <= today:
        if date.weekday() < 5:
            need_dates.append(date.strftime("%Y/%m/%d"))
        date += timedelta(days=1)

    return need_dates

def check_filename_legal(filename):
    # Remove characters that are not alphanumeric, spaces, dots, underscores, or Chinese characters
    legal_filename = re.sub(r'[^\w\s._\u4e00-\u9fff]', '', filename)
    return legal_filename.rstrip()

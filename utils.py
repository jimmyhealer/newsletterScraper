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
def working_days_between(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
    end_date = datetime.strptime(end_date_str, "%Y/%m/%d")

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    working_days = 0

    while start_date <= end_date:
        if start_date.weekday() < 5:  # Monday to Friday are working days
            working_days += 1
        start_date += timedelta(days=1)

    return working_days

def add_working_day(start_date_str, end_date_str=None):
    if end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
        end_date = datetime.strptime(end_date_str, "%Y/%m/%d")
    else:
        start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
        end_date = datetime.today()

    need_dates = []

    while start_date <= end_date:
        if start_date.weekday() < 5:
            need_dates.append(start_date.strftime("%Y/%m/%d"))
        start_date += timedelta(days=1)

    return need_dates

def check_filename_legal(filename):
    # Remove characters that are not alphanumeric, spaces, dots, underscores, or Chinese characters
    legal_filename = re.sub(r'[^\w\s._\u4e00-\u9fff]', '', filename)
    return legal_filename.rstrip()

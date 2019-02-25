from datetime import timedelta


def get_week_dates(date):
    week_day = date.isocalendar()[2]
    current_date = date
    current_week_day = week_day

    week_dates = [current_date]

    while current_week_day <= week_day:
        current_date -= timedelta(days=1)
        current_week_day = current_date.isocalendar()[2]
        week_dates.append(current_date)

        if current_week_day == 1:
            break

    if len(week_dates) < 7:
        current_date = date
        for i in range(len(week_dates), 7):
            current_date += timedelta(days=1)
            week_dates.append(current_date)
    return week_dates


def get_first_date_of_week_dates(week_dates):
    for date in week_dates:
        if date.isocalendar()[2] == 1:
            return date

from datetime import date, datetime

from django.utils.timezone import utc


def start_month_date():
    first_date_of_month = (
        datetime.combine(
            date.today().replace(day=1),
            datetime.min.time()
        )
    ).replace(tzinfo=utc)
    return first_date_of_month

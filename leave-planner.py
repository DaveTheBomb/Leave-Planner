from calendar import day_name, weekday
from datetime import date
import holidays


def get_holidays(year):
    """Return a sorted list of (date, name) tuples for South African public holidays."""
    south_africa_holidays = holidays.SouthAfrica(years=year)
    return sorted(south_africa_holidays.items())


def get_holiday_dates(year):
    """Return a sorted list of date objects for South African public holidays."""
    return [date(d.year, d.month, d.day) for d, _ in get_holidays(year)]


def get_day_of_week(d):
    """Return the day-of-week name (e.g. 'Monday') for a given date."""
    return day_name[weekday(d.year, d.month, d.day)]


def calculate_gaps(holiday_dates):
    """
    Given a list of dates, return a list of gap entries between consecutive dates.
    Each entry is [leave_days_needed, from_label, to_label] where leave_days_needed
    is the number of working days between the two holidays (total days - 1).
    """
    gaps = []
    for index in range(len(holiday_dates) - 1):
        date_one = holiday_dates[index]
        date_two = holiday_dates[index + 1]
        day_one = get_day_of_week(date_one)
        day_two = get_day_of_week(date_two)
        days_difference = (date_two - date_one).days
        gaps.append([
            days_difference - 1,
            f"{day_one:<10} {date_one}",
            f"{day_two:<10} {date_two}"
        ])
    return gaps


def filter_gaps_by_leave(gaps, available_leave_days):
    """Return only the gaps that can be bridged with the given number of leave days."""
    return [gap for gap in gaps if gap[0] <= available_leave_days]


def main():
    print("*************************************************************************************")

    while True:
        try:
            year = int(input("Enter year: "))
            break
        except ValueError:
            print("Enter a valid year, an integer.")

    holiday_list = get_holidays(year)
    holiday_dates = []

    for datei, name in holiday_list:
        d = date(datei.year, datei.month, datei.day)
        day_of_week = get_day_of_week(d)
        holiday_dates.append(d)
        print(f"{day_of_week:<10} {datei} {name}")

    print("*************************************************************************************")

    gaps = calculate_gaps(holiday_dates)

    for gap in gaps:
        days_total = gap[0] + 1
        print(f"{gap[1]}  {gap[2]}     {days_total} days")

    print("*************************************************************************************")

    while True:
        try:
            number_of_leave_days = int(input("Enter number of leave days available: "))
            break
        except ValueError:
            print("Enter a valid number, an integer.")

    for potential_days in filter_gaps_by_leave(gaps, number_of_leave_days):
        print(potential_days)


if __name__ == "__main__":
    main()

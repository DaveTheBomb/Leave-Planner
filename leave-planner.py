from calendar import day_name, weekday
from datetime import date, timedelta
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


def is_weekend(d):
    """Return True if the date falls on a Saturday or Sunday."""
    return d.weekday() >= 5


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


def calculate_break_length(date_one, date_two, holiday_dates):
    """
    Given two public holidays and the full list of holiday dates, calculate the
    total length of the continuous break you get by taking leave between them.

    Logic:
      1. Walk backwards from date_one to include any attached weekend days or
         public holidays before it (extending the break start).
      2. Walk forwards from date_two to include any attached weekend days or
         public holidays after it (extending the break end).
      3. Count only the weekdays between date_one and date_two (exclusive) that
         are not themselves public holidays — these are the leave days needed.
      4. Total break = (break_end - break_start).days + 1

    Returns a dict with:
      - leave_days_needed: int
      - total_break_days: int
      - break_start: date
      - break_end: date
    """
    holiday_set = set(holiday_dates)

    # Extend break start backwards past weekends and holidays
    break_start = date_one
    while True:
        prev_day = break_start - timedelta(days=1)
        if is_weekend(prev_day) or prev_day in holiday_set:
            break_start = prev_day
        else:
            break

    # Extend break end forwards past weekends and holidays
    break_end = date_two
    while True:
        next_day = break_end + timedelta(days=1)
        if is_weekend(next_day) or next_day in holiday_set:
            break_end = next_day
        else:
            break

    # Count leave days needed: weekdays strictly between the two holidays
    # that are not public holidays
    leave_days_needed = 0
    current = date_one + timedelta(days=1)
    while current < date_two:
        if not is_weekend(current) and current not in holiday_set:
            leave_days_needed += 1
        current += timedelta(days=1)

    total_break_days = (break_end - break_start).days + 1

    return {
        "leave_days_needed": leave_days_needed,
        "total_break_days": total_break_days,
        "break_start": break_start,
        "break_end": break_end,
    }


def filter_gaps_by_leave(gaps, available_leave_days):
    """Return only the gaps that can be bridged with the given number of leave days."""
    return [gap for gap in gaps if gap[0] <= available_leave_days]


def compute_break_for_window(leave_start, leave_end, holiday_set):
    """
    Given a window of leave days (leave_start to leave_end inclusive),
    extend the break backwards and forwards over weekends and holidays,
    then return a dict describing the full continuous break.
    """
    # Extend backwards
    break_start = leave_start
    while True:
        prev = break_start - timedelta(days=1)
        if is_weekend(prev) or prev in holiday_set:
            break_start = prev
        else:
            break

    # Extend forwards
    break_end = leave_end
    while True:
        nxt = break_end + timedelta(days=1)
        if is_weekend(nxt) or nxt in holiday_set:
            break_end = nxt
        else:
            break

    # Count actual leave days used in the window (excludes weekends/holidays)
    leave_days_used = 0
    current = leave_start
    while current <= leave_end:
        if not is_weekend(current) and current not in holiday_set:
            leave_days_used += 1
        current += timedelta(days=1)

    total_break_days = (break_end - break_start).days + 1

    return {
        "leave_days_needed": leave_days_used,
        "total_break_days": total_break_days,
        "break_start": break_start,
        "break_end": break_end,
        "leave_start": leave_start,
        "leave_end": leave_end,
    }


def find_all_breaks(year, available_leave_days):
    """
    Slide a window of exactly `available_leave_days` leave days across every
    weekday in the year. For each placement, compute the full continuous break
    (including attached weekends and public holidays). Deduplicate by
    (break_start, break_end) and remove dominated breaks — those whose date
    range is fully contained within a longer break achievable with the same
    or fewer leave days.

    Returns results sorted by total_break_days descending.
    """
    holiday_dates = get_holiday_dates(year)
    holiday_set = set(holiday_dates)

    # Build the list of all workdays (weekdays that are not public holidays)
    workdays = []
    current = date(year, 1, 1)
    end_of_year = date(year, 12, 31)
    while current <= end_of_year:
        if not is_weekend(current) and current not in holiday_set:
            workdays.append(current)
        current += timedelta(days=1)

    seen = {}  # key: (break_start, break_end) -> best result

    # Slide a window of exactly `available_leave_days` workdays
    n = available_leave_days

    # Guard against invalid input
    if n < 0:
        return []
    if n == 0:
        # No leave days: check each holiday/weekend cluster for free breaks
        for h in holiday_dates:
            result = compute_break_for_window(h, h, holiday_set)
            key = (result["break_start"], result["break_end"])
            if key not in seen or result["total_break_days"] > seen[key]["total_break_days"]:
                seen[key] = result
    else:
        for i in range(len(workdays) - n + 1):
            leave_start = workdays[i]
            leave_end = workdays[i + n - 1]
            result = compute_break_for_window(leave_start, leave_end, holiday_set)
            if result["leave_days_needed"] <= available_leave_days:
                key = (result["break_start"], result["break_end"])
                if key not in seen or result["leave_days_needed"] < seen[key]["leave_days_needed"]:
                    seen[key] = result

    candidates = list(seen.values())

    # Remove dominated breaks: if break A is fully contained within break B
    # and B costs no more leave days than A, then A is dominated and should
    # be dropped — it is a strictly worse option.
    def is_dominated(a, all_breaks):
        for b in all_breaks:
            if b is a:
                continue
            if (b["break_start"] <= a["break_start"]
                    and b["break_end"] >= a["break_end"]
                    and b["total_break_days"] > a["total_break_days"]
                    and b["leave_days_needed"] <= a["leave_days_needed"]):
                return True
        return False

    # Only keep breaks that are better than the plain baseline:
    # The best you can get from N leave days with no holiday help is:
    # 2 weekend days before + N leave days + 2 weekend days after = N + 4.
    # Any break that doesn't beat this is just a plain work week and adds
    # no strategic value.
    def beats_baseline(b):
        if n == 0:
            return True
        return b["total_break_days"] > n + 4

    results = [b for b in candidates if not is_dominated(b, candidates) and beats_baseline(b)]
    results.sort(key=lambda x: x["total_break_days"], reverse=True)
    return results


def validate_year(value):
    """
    Validate a year input.
    - Must be convertible to an integer.
    - Must be between 2000 and 2100 (inclusive).
    Returns (int, None) on success or (None, error_message) on failure.
    """
    try:
        year = int(value)
    except (ValueError, TypeError):
        return None, "Invalid input. Please enter a whole number for the year."
    if year < 2000 or year > 2100:
        return None, "Year must be between 2000 and 2100."
    return year, None


def validate_leave_days(value):
    """
    Validate a leave days input.
    - Must be convertible to an integer.
    - Must be between 0 and 365 (inclusive).
    Returns (int, None) on success or (None, error_message) on failure.
    """
    try:
        days = int(value)
    except (ValueError, TypeError):
        return None, "Invalid input. Please enter a whole number for leave days."
    if days < 0:
        return None, "Leave days cannot be negative."
    if days > 365:
        return None, "Leave days cannot exceed 365."
    return days, None


def get_best_breaks(holiday_dates, available_leave_days):
    """
    For each consecutive pair of holidays that can be bridged with available leave days,
    calculate the full break length (including attached weekends).
    Returns a list of break dicts sorted by total_break_days descending.
    """
    breaks = []
    for index in range(len(holiday_dates) - 1):
        date_one = holiday_dates[index]
        date_two = holiday_dates[index + 1]
        result = calculate_break_length(date_one, date_two, holiday_dates)
        if result["leave_days_needed"] <= available_leave_days:
            result["holiday_start"] = date_one
            result["holiday_end"] = date_two
            breaks.append(result)

    breaks.sort(key=lambda x: x["total_break_days"], reverse=True)
    return breaks


def main():
    print("*************************************************************************************")

    while True:
        year, error = validate_year(input("Enter year: "))
        if error:
            print(f"  Error: {error}")
        else:
            break

    holiday_list = get_holidays(year)
    holiday_dates = []

    for datei, name in holiday_list:
        d = date(datei.year, datei.month, datei.day)
        day_of_week = get_day_of_week(d)
        holiday_dates.append(d)
        print(f"{day_of_week:<10} {datei} {name}")

    print("*************************************************************************************")

    while True:
        number_of_leave_days, error = validate_leave_days(input("Enter number of leave days available: "))
        if error:
            print(f"  Error: {error}")
        else:
            break

    best_breaks = find_all_breaks(year, number_of_leave_days)

    if not best_breaks:
        print("No breaks found with your available leave days.")
        return

    print(f"\nTop breaks you can get with {number_of_leave_days} leave day(s), ranked by length:\n")
    for i, b in enumerate(best_breaks, start=1):
        if number_of_leave_days == 0:
            leave_info = "no leave days needed"
        else:
            leave_info = (
                f"use {b['leave_days_needed']} leave day(s): "
                f"{b['leave_start']} to {b['leave_end']}"
            )
        print(
            f"  {i}. {b['total_break_days']}-day break  "
            f"({b['break_start']} to {b['break_end']})  "
            f"| {leave_info}"
        )

    print("\n*************************************************************************************")


if __name__ == "__main__":
    main()

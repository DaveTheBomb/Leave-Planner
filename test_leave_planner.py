import unittest
import importlib
from datetime import date

# The module filename uses a hyphen, so standard import won't work — use importlib
lp = importlib.import_module("leave-planner")
get_holidays = lp.get_holidays
get_holiday_dates = lp.get_holiday_dates
get_day_of_week = lp.get_day_of_week
calculate_gaps = lp.calculate_gaps
filter_gaps_by_leave = lp.filter_gaps_by_leave
is_weekend = lp.is_weekend
calculate_break_length = lp.calculate_break_length
get_best_breaks = lp.get_best_breaks
validate_year = lp.validate_year
validate_leave_days = lp.validate_leave_days
compute_break_for_window = lp.compute_break_for_window
find_all_breaks = lp.find_all_breaks


class TestGetHolidays(unittest.TestCase):

    def test_returns_list_of_tuples(self):
        result = get_holidays(2026)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for item in result:
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[1], str)

    def test_sorted_order(self):
        result = get_holidays(2026)
        dates = [d for d, _ in result]
        self.assertEqual(dates, sorted(dates))

    def test_known_holiday_present(self):
        result = get_holidays(2026)
        names = [name for _, name in result]
        self.assertTrue(any("New Year" in name for name in names))


class TestGetHolidayDates(unittest.TestCase):

    def test_returns_list_of_dates(self):
        result = get_holiday_dates(2026)
        self.assertIsInstance(result, list)
        for d in result:
            self.assertIsInstance(d, date)

    def test_new_years_day_present(self):
        result = get_holiday_dates(2026)
        self.assertIn(date(2026, 1, 1), result)

    def test_sorted_order(self):
        result = get_holiday_dates(2026)
        self.assertEqual(result, sorted(result))


class TestGetDayOfWeek(unittest.TestCase):

    def test_known_monday(self):
        # 2026-01-05 is a Monday
        self.assertEqual(get_day_of_week(date(2026, 1, 5)), "Monday")

    def test_known_friday(self):
        # 2026-01-02 is a Friday
        self.assertEqual(get_day_of_week(date(2026, 1, 2)), "Friday")

    def test_known_thursday(self):
        # 2026-01-01 is a Thursday
        self.assertEqual(get_day_of_week(date(2026, 1, 1)), "Thursday")

    def test_returns_string(self):
        result = get_day_of_week(date(2026, 6, 15))
        self.assertIsInstance(result, str)


class TestCalculateGaps(unittest.TestCase):

    def test_gap_count(self):
        dates = [date(2026, 1, 1), date(2026, 1, 10), date(2026, 1, 20)]
        gaps = calculate_gaps(dates)
        self.assertEqual(len(gaps), 2)

    def test_gap_days_calculation(self):
        dates = [date(2026, 1, 1), date(2026, 1, 6)]
        gaps = calculate_gaps(dates)
        # 6 - 1 = 5 total days, leave needed = 5 - 1 = 4
        self.assertEqual(gaps[0][0], 4)

    def test_adjacent_dates_zero_leave_needed(self):
        dates = [date(2026, 1, 1), date(2026, 1, 2)]
        gaps = calculate_gaps(dates)
        self.assertEqual(gaps[0][0], 0)

    def test_empty_list(self):
        self.assertEqual(calculate_gaps([]), [])

    def test_single_date(self):
        self.assertEqual(calculate_gaps([date(2026, 1, 1)]), [])

    def test_gap_contains_labels(self):
        dates = [date(2026, 1, 1), date(2026, 1, 6)]
        gaps = calculate_gaps(dates)
        self.assertEqual(len(gaps[0]), 3)
        self.assertIn("2026-01-01", gaps[0][1])
        self.assertIn("2026-01-06", gaps[0][2])


class TestFilterGapsByLeave(unittest.TestCase):

    def setUp(self):
        self.gaps = [
            [0, "from_a", "to_a"],
            [3, "from_b", "to_b"],
            [5, "from_c", "to_c"],
            [10, "from_d", "to_d"],
        ]

    def test_filter_exact_match(self):
        result = filter_gaps_by_leave(self.gaps, 5)
        self.assertEqual(len(result), 3)  # 0, 3, 5

    def test_filter_zero_leave(self):
        result = filter_gaps_by_leave(self.gaps, 0)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 0)

    def test_filter_all(self):
        result = filter_gaps_by_leave(self.gaps, 10)
        self.assertEqual(len(result), 4)

    def test_filter_none(self):
        result = filter_gaps_by_leave(self.gaps, -1)
        self.assertEqual(len(result), 0)

    def test_empty_gaps(self):
        self.assertEqual(filter_gaps_by_leave([], 5), [])


class TestIsWeekend(unittest.TestCase):

    def test_saturday_is_weekend(self):
        # 2026-01-03 is a Saturday
        self.assertTrue(is_weekend(date(2026, 1, 3)))

    def test_sunday_is_weekend(self):
        # 2026-01-04 is a Sunday
        self.assertTrue(is_weekend(date(2026, 1, 4)))

    def test_monday_is_not_weekend(self):
        # 2026-01-05 is a Monday
        self.assertFalse(is_weekend(date(2026, 1, 5)))

    def test_friday_is_not_weekend(self):
        # 2026-01-02 is a Friday
        self.assertFalse(is_weekend(date(2026, 1, 2)))


class TestCalculateBreakLength(unittest.TestCase):

    def test_zero_leave_days_adjacent_holidays(self):
        # Thursday 2026-01-01 and Friday 2026-01-02: no weekdays between them
        holiday_dates = [date(2026, 1, 1), date(2026, 1, 2)]
        result = calculate_break_length(date(2026, 1, 1), date(2026, 1, 2), holiday_dates)
        self.assertEqual(result["leave_days_needed"], 0)

    def test_break_extends_backwards_over_weekend(self):
        # Holiday on Monday 2026-01-05: break should extend back to Saturday 2026-01-03
        holiday_dates = [date(2026, 1, 5), date(2026, 1, 26)]
        result = calculate_break_length(date(2026, 1, 5), date(2026, 1, 26), holiday_dates)
        self.assertEqual(result["break_start"], date(2026, 1, 3))  # Saturday before Monday

    def test_break_extends_forwards_over_weekend(self):
        # Holiday on Friday 2026-01-02: break should extend forward to Sunday 2026-01-04
        holiday_dates = [date(2026, 1, 1), date(2026, 1, 2)]
        result = calculate_break_length(date(2026, 1, 1), date(2026, 1, 2), holiday_dates)
        self.assertEqual(result["break_end"], date(2026, 1, 4))  # Sunday after Friday

    def test_leave_days_excludes_weekends(self):
        # 2026-01-08 (Thursday) to 2026-01-16 (Friday):
        # weekdays between: Fri 9, Mon 12, Tue 13, Wed 14, Thu 15 = 5 leave days
        holiday_dates = [date(2026, 1, 8), date(2026, 1, 16)]
        result = calculate_break_length(date(2026, 1, 8), date(2026, 1, 16), holiday_dates)
        self.assertEqual(result["leave_days_needed"], 5)

    def test_total_break_days_is_positive(self):
        holiday_dates = [date(2026, 1, 1), date(2026, 1, 26)]
        result = calculate_break_length(date(2026, 1, 1), date(2026, 1, 26), holiday_dates)
        self.assertGreater(result["total_break_days"], 0)

    def test_break_start_lte_holiday_start(self):
        holiday_dates = [date(2026, 1, 1), date(2026, 1, 26)]
        result = calculate_break_length(date(2026, 1, 1), date(2026, 1, 26), holiday_dates)
        self.assertLessEqual(result["break_start"], date(2026, 1, 1))

    def test_break_end_gte_holiday_end(self):
        holiday_dates = [date(2026, 1, 1), date(2026, 1, 26)]
        result = calculate_break_length(date(2026, 1, 1), date(2026, 1, 26), holiday_dates)
        self.assertGreaterEqual(result["break_end"], date(2026, 1, 26))

    def test_returns_required_keys(self):
        holiday_dates = [date(2026, 1, 1), date(2026, 1, 2)]
        result = calculate_break_length(date(2026, 1, 1), date(2026, 1, 2), holiday_dates)
        self.assertIn("leave_days_needed", result)
        self.assertIn("total_break_days", result)
        self.assertIn("break_start", result)
        self.assertIn("break_end", result)

    def test_leave_days_excludes_public_holidays_in_gap(self):
        # If a public holiday falls within the gap, it should not count as a leave day
        # 2026-01-01 (Thu) → 2026-01-26 (Mon), with 2026-01-02 (Fri) also a holiday
        holiday_dates = [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 26)]
        result = calculate_break_length(date(2026, 1, 1), date(2026, 1, 2), holiday_dates)
        # No weekdays between Jan 1 and Jan 2 that aren't holidays
        self.assertEqual(result["leave_days_needed"], 0)


class TestGetBestBreaks(unittest.TestCase):

    def test_returns_list(self):
        holiday_dates = get_holiday_dates(2026)
        result = get_best_breaks(holiday_dates, 5)
        self.assertIsInstance(result, list)

    def test_sorted_by_total_break_days_descending(self):
        holiday_dates = get_holiday_dates(2026)
        result = get_best_breaks(holiday_dates, 10)
        totals = [b["total_break_days"] for b in result]
        self.assertEqual(totals, sorted(totals, reverse=True))

    def test_all_results_within_leave_budget(self):
        holiday_dates = get_holiday_dates(2026)
        available = 3
        result = get_best_breaks(holiday_dates, available)
        for b in result:
            self.assertLessEqual(b["leave_days_needed"], available)

    def test_zero_leave_days_returns_free_bridges_only(self):
        holiday_dates = get_holiday_dates(2026)
        result = get_best_breaks(holiday_dates, 0)
        for b in result:
            self.assertEqual(b["leave_days_needed"], 0)

    def test_no_breaks_when_leave_is_negative(self):
        holiday_dates = get_holiday_dates(2026)
        result = get_best_breaks(holiday_dates, -1)
        self.assertEqual(result, [])

    def test_each_result_has_required_keys(self):
        holiday_dates = get_holiday_dates(2026)
        result = get_best_breaks(holiday_dates, 5)
        for b in result:
            self.assertIn("leave_days_needed", b)
            self.assertIn("total_break_days", b)
            self.assertIn("break_start", b)
            self.assertIn("break_end", b)
            self.assertIn("holiday_start", b)
            self.assertIn("holiday_end", b)


class TestValidateYear(unittest.TestCase):

    def test_valid_year(self):
        year, error = validate_year("2026")
        self.assertEqual(year, 2026)
        self.assertIsNone(error)

    def test_lower_boundary(self):
        year, error = validate_year("2000")
        self.assertEqual(year, 2000)
        self.assertIsNone(error)

    def test_upper_boundary(self):
        year, error = validate_year("2100")
        self.assertEqual(year, 2100)
        self.assertIsNone(error)

    def test_year_too_low(self):
        year, error = validate_year("1999")
        self.assertIsNone(year)
        self.assertIsNotNone(error)

    def test_year_too_high(self):
        year, error = validate_year("2101")
        self.assertIsNone(year)
        self.assertIsNotNone(error)

    def test_non_integer_string(self):
        year, error = validate_year("abc")
        self.assertIsNone(year)
        self.assertIsNotNone(error)

    def test_float_string(self):
        year, error = validate_year("2026.5")
        self.assertIsNone(year)
        self.assertIsNotNone(error)

    def test_empty_string(self):
        year, error = validate_year("")
        self.assertIsNone(year)
        self.assertIsNotNone(error)

    def test_none_input(self):
        year, error = validate_year(None)
        self.assertIsNone(year)
        self.assertIsNotNone(error)

    def test_negative_year(self):
        year, error = validate_year("-100")
        self.assertIsNone(year)
        self.assertIsNotNone(error)


class TestValidateLeaveDays(unittest.TestCase):

    def test_valid_leave_days(self):
        days, error = validate_leave_days("10")
        self.assertEqual(days, 10)
        self.assertIsNone(error)

    def test_zero_leave_days(self):
        days, error = validate_leave_days("0")
        self.assertEqual(days, 0)
        self.assertIsNone(error)

    def test_max_leave_days(self):
        days, error = validate_leave_days("365")
        self.assertEqual(days, 365)
        self.assertIsNone(error)

    def test_negative_leave_days(self):
        days, error = validate_leave_days("-1")
        self.assertIsNone(days)
        self.assertIsNotNone(error)

    def test_exceeds_max_leave_days(self):
        days, error = validate_leave_days("366")
        self.assertIsNone(days)
        self.assertIsNotNone(error)

    def test_non_integer_string(self):
        days, error = validate_leave_days("five")
        self.assertIsNone(days)
        self.assertIsNotNone(error)

    def test_float_string(self):
        days, error = validate_leave_days("5.5")
        self.assertIsNone(days)
        self.assertIsNotNone(error)

    def test_empty_string(self):
        days, error = validate_leave_days("")
        self.assertIsNone(days)
        self.assertIsNotNone(error)

    def test_none_input(self):
        days, error = validate_leave_days(None)
        self.assertIsNone(days)
        self.assertIsNotNone(error)


class TestComputeBreakForWindow(unittest.TestCase):

    def test_returns_required_keys(self):
        holiday_set = set()
        # 2026-01-12 Monday to 2026-01-14 Wednesday
        result = compute_break_for_window(date(2026, 1, 12), date(2026, 1, 14), holiday_set)
        for key in ["leave_days_needed", "total_break_days", "break_start", "break_end", "leave_start", "leave_end"]:
            self.assertIn(key, result)

    def test_extends_backwards_over_weekend(self):
        # Leave starts Monday 2026-01-05: break should reach back to Saturday 2026-01-03
        holiday_set = set()
        result = compute_break_for_window(date(2026, 1, 5), date(2026, 1, 7), holiday_set)
        self.assertEqual(result["break_start"], date(2026, 1, 3))

    def test_extends_forwards_over_weekend(self):
        # Leave ends Friday 2026-01-09: break should extend to Sunday 2026-01-11
        holiday_set = set()
        result = compute_break_for_window(date(2026, 1, 7), date(2026, 1, 9), holiday_set)
        self.assertEqual(result["break_end"], date(2026, 1, 11))

    def test_leave_days_excludes_weekends_in_window(self):
        # Window Mon 2026-01-05 to Fri 2026-01-09: 5 workdays, no holidays
        holiday_set = set()
        result = compute_break_for_window(date(2026, 1, 5), date(2026, 1, 9), holiday_set)
        self.assertEqual(result["leave_days_needed"], 5)

    def test_leave_days_excludes_holidays_in_window(self):
        # Window Mon 2026-03-30 to Fri 2026-04-03: Good Friday (Apr 3) is a holiday
        holiday_set = {date(2026, 4, 3)}
        result = compute_break_for_window(date(2026, 3, 30), date(2026, 4, 3), holiday_set)
        # Mon, Tue, Wed, Thu = 4 leave days (Good Friday excluded)
        self.assertEqual(result["leave_days_needed"], 4)

    def test_total_break_days_greater_than_window(self):
        # Any window touching a weekend should yield more total days than workdays used
        holiday_set = set()
        result = compute_break_for_window(date(2026, 1, 5), date(2026, 1, 9), holiday_set)
        self.assertGreater(result["total_break_days"], result["leave_days_needed"])


class TestFindAllBreaks(unittest.TestCase):

    def test_returns_list(self):
        result = find_all_breaks(2026, 5)
        self.assertIsInstance(result, list)

    def test_sorted_by_total_break_days_descending(self):
        result = find_all_breaks(2026, 5)
        totals = [b["total_break_days"] for b in result]
        self.assertEqual(totals, sorted(totals, reverse=True))

    def test_all_results_within_leave_budget(self):
        available = 3
        result = find_all_breaks(2026, available)
        for b in result:
            self.assertLessEqual(b["leave_days_needed"], available)

    def test_finds_11_day_break_with_5_leave_days(self):
        # Taking 5 leave days from 27 Mar 2026 should yield an 11-day break
        result = find_all_breaks(2026, 5)
        eleven_day = [
            b for b in result
            if b["break_start"] == date(2026, 3, 27) and b["break_end"] == date(2026, 4, 6)
        ]
        self.assertTrue(len(eleven_day) > 0, "Expected 11-day break (27 Mar – 6 Apr) not found")
        self.assertEqual(eleven_day[0]["total_break_days"], 11)

    def test_no_breaks_for_negative_leave(self):
        result = find_all_breaks(2026, -1)
        self.assertEqual(result, [])

    def test_zero_leave_returns_free_clusters(self):
        result = find_all_breaks(2026, 0)
        for b in result:
            self.assertEqual(b["leave_days_needed"], 0)

    def test_each_result_has_required_keys(self):
        result = find_all_breaks(2026, 3)
        for b in result:
            for key in ["leave_days_needed", "total_break_days", "break_start", "break_end", "leave_start", "leave_end"]:
                self.assertIn(key, b)

    def test_no_duplicate_break_windows(self):
        result = find_all_breaks(2026, 5)
        keys = [(b["break_start"], b["break_end"]) for b in result]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()

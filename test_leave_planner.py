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


class TestGetHolidays(unittest.TestCase):

    def test_returns_list_of_tuples(self):
        result = get_holidays(2026)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        # Each item should be a (date, str) tuple
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
        # n dates → n-1 gaps
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
        # Each gap entry has 3 elements: [leave_days, from_label, to_label]
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


if __name__ == "__main__":
    unittest.main()

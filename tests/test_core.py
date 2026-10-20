"""Deterministic tests for timestamp_parser_range_py.core.parse_timestamp."""

import unittest

from timestamp_parser_range_py import ParseResult, parse_timestamp


class TestParseTimestamp(unittest.TestCase):
    def test_full_utc_z(self):
        r = parse_timestamp("2024-01-02T03:04:05.6789Z")
        self.assertEqual(r.year, 2024)
        self.assertEqual(r.month, 1)
        self.assertEqual(r.day, 2)
        self.assertEqual(r.hour, 3)
        self.assertEqual(r.minute, 4)
        self.assertEqual(r.second, 5)
        self.assertEqual(r.nanosecond, 678_900_000)
        self.assertEqual(r.offset_minutes, 0)

    def test_explicit_positive_offset(self):
        r = parse_timestamp("2024-01-02T03:04:05+09:30")
        self.assertEqual(r.offset_minutes, 570)
        self.assertEqual(r.nanosecond, 0)

    def test_explicit_negative_offset(self):
        r = parse_timestamp("2024-01-02T03:04:05-08:00")
        self.assertEqual(r.offset_minutes, -480)

    def test_z_and_offset_are_equivalent_for_utc(self):
        z = parse_timestamp("2024-06-01T00:00:00Z")
        o = parse_timestamp("2024-06-01T00:00:00+00:00")
        self.assertEqual(z, o)

    def test_missing_offset_defaults_to_zero(self):
        r = parse_timestamp("2024-06-01T00:00:00")
        self.assertEqual(r.offset_minutes, 0)

    def test_fractional_pads_to_nanoseconds(self):
        self.assertEqual(parse_timestamp("2024-01-02T03:04:05.5").nanosecond, 500_000_000)
        self.assertEqual(parse_timestamp("2024-01-02T03:04:05.05").nanosecond, 50_000_000)
        self.assertEqual(parse_timestamp("2024-01-02T03:04:05.123456789").nanosecond, 123_456_789)

    def test_max_nine_fractional_digits(self):
        self.assertEqual(parse_timestamp("2024-01-02T03:04:05.999999999").nanosecond, 999_999_999)

    def test_leap_second_rejected(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2016-12-31T23:59:60Z")

    def test_rejects_space_separator(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02 03:04:05Z")

    def test_rejects_comma_decimal(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02T03:04:05,5Z")

    def test_rejects_basic_format(self):
        with self.assertRaises(ValueError):
            parse_timestamp("20240102T030405Z")

    def test_rejects_trailing_characters(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02T03:04:05Zjunk")

    def test_rejects_empty_string(self):
        with self.assertRaises(ValueError):
            parse_timestamp("")

    def test_rejects_non_string(self):
        with self.assertRaises(ValueError):
            parse_timestamp(None)

    def test_rejects_short_offset(self):
        with self.assertRaises(ValueError):
            parse_timestamp("2024-01-02T03:04:05+08")

    def test_returns_pareresult(self):
        self.assertIsInstance(parse_timestamp("2024-01-02T03:04:05Z"), ParseResult)


if __name__ == "__main__":
    unittest.main()

"""Tests for the cron expression parser (standard library only)."""

import subprocess
import sys
import unittest
from pathlib import Path

from cron_parser import expand_field, format_table, parse_cron


class FieldExpansionTests(unittest.TestCase):
    def test_wildcard(self):
        self.assertEqual(expand_field("*", 1, 3), [1, 2, 3])

    def test_step(self):
        self.assertEqual(expand_field("*/15", 0, 59), [0, 15, 30, 45])

    def test_range(self):
        self.assertEqual(expand_field("1-5", 0, 7), [1, 2, 3, 4, 5])

    def test_list_deduplicated_and_sorted(self):
        self.assertEqual(expand_field("15,1,15", 1, 31), [1, 15])

    def test_range_with_step(self):
        self.assertEqual(expand_field("1-10/2", 0, 59), [1, 3, 5, 7, 9])

    def test_start_with_step(self):
        self.assertEqual(expand_field("5/20", 0, 59), [5, 25, 45])

    def test_invalid_terms(self):
        for expression in ("", "1,", "*/0", "*/x", "1-", "5-1", "60", "-1", "1/2/3"):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    expand_field(expression, 0, 59)


class ParserTests(unittest.TestCase):
    def test_example_output(self):
        expression = "*/15 0 1,15 * 1-5 /usr/bin/find"
        expected = (
            "minute        0 15 30 45\n"
            "hour          0\n"
            "day of month  1 15\n"
            "month         1 2 3 4 5 6 7 8 9 10 11 12\n"
            "day of week   1 2 3 4 5\n"
            "command       /usr/bin/find"
        )
        self.assertEqual(format_table(parse_cron(expression)), expected)

    def test_command_with_arguments(self):
        self.assertEqual(parse_cron("0 0 * * * /bin/echo hello world")[-1],
                         ("command", "/bin/echo hello world"))

    def test_sunday_alias(self):
        self.assertEqual(parse_cron("0 0 * * 0,7 echo hi")[4], ("day of week", "0"))

    def test_missing_command(self):
        with self.assertRaises(ValueError):
            parse_cron("0 0 * * *")

    def test_invalid_month(self):
        with self.assertRaises(ValueError):
            parse_cron("0 0 * 13 * echo hi")

    def test_cli_error_exit(self):
        script = Path(__file__).with_name("cron_parser.py")
        result = subprocess.run([sys.executable, str(script), "bad"],
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stderr)


if __name__ == "__main__":
    unittest.main()

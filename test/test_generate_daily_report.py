import unittest
from library.caterlord.generate_daily_report import generate_daily_report

class MyTestCase(unittest.TestCase):
    def test_generate_daily_report(self):
        self.assertEqual(True, generate_daily_report(2025, 3))  # add assertion here


if __name__ == '__main__':
    unittest.main()

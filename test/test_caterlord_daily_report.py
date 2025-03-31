import unittest
from library.caterlord.generate_daily_report import daily_report

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, daily_report())  # add assertion here


if __name__ == '__main__':
    unittest.main()

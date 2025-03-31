import unittest
from library.caterlord.tlp_csv_parser import data_importer

class MyTestCaterlordDailyReportCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, data_importer())  # add assertion here


if __name__ == '__main__':
    unittest.main()

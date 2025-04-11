import unittest
from library.caterlord.daily_push_msg import daily_push_msg

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, daily_push_msg())  # add assertion here


if __name__ == '__main__':
    unittest.main()

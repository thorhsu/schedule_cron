import unittest
from library.caterlord.jgg_franchise_updater import update_shop_franchise


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, update_shop_franchise())  # add assertion here


if __name__ == '__main__':
    unittest.main()

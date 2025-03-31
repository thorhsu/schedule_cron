import datetime
import unittest
from smbclient import  register_session, scandir, copyfile
from library.caterlord.get_remote_files import get_remote_files


class MySambaCase(unittest.TestCase):
    def test_connect(self):
        get_remote_files()



import datetime
import unittest
from smbclient import  register_session, scandir, copyfile
from library.caterlord.get_remote_files import get_remote_files
from library.caterlord.receive_gmail import download_mail_attach


class MySambaCase(unittest.TestCase):
    def test_receive_mail(self):
        self.assertEqual(True, download_mail_attach())


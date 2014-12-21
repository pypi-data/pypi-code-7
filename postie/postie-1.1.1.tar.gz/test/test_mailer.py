import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from postie import Mailer


class TestMailer(unittest.TestCase):
    def test_empty(self):
        mailer = Mailer()

    def test_invalid_server_types(self):
        combinations = [
            dict(use_ssl=True, use_starttls=True),
            dict(use_starttls=True, use_lmtp=True),
            dict(use_ssl=True, use_lmtp=True),
            dict(use_ssl=True, use_starttls=True, use_lmtp=True),
        ]

        for kwargs in combinations:
            mailer = Mailer(**kwargs)
            def raises():
                with mailer:
                    pass
            self.assertRaises(ValueError, raises)

    def test_os_environ(self):
        os.environ["MAIL_HOST"] = "localhost"
        os.environ["MAIL_PORT"] = "123"
        os.environ["MAIL_USE_STARTTLS"] = "yes"

        mailer = Mailer.from_environ()
        self.assertEqual(mailer.host, "localhost")
        self.assertEqual(mailer.port, 123)
        self.assertEqual(mailer.use_ssl, False)
        self.assertEqual(mailer.use_starttls, True)
        self.assertEqual(mailer.use_lmtp, False)

    def test_dict_environ(self):
        environ = {
            "MAIL_HOST": "localhost",
            "MAIL_PORT": "123",
            "MAIL_USE_SSL": "yes"
        }

        mailer = Mailer.from_environ(environ=environ)
        self.assertEqual(mailer.host, "localhost")
        self.assertEqual(mailer.port, 123)
        self.assertEqual(mailer.use_ssl, True)
        self.assertEqual(mailer.use_starttls, False)
        self.assertEqual(mailer.use_lmtp, False)

from test_settings import CloudFSTestCase
from cloudfs.session import Session
from cloudfs import errors

import unittest
import string
import random


class AuthenticationTests(CloudFSTestCase):

    def test_authenticate(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

    def test_ping(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.assertEqual(False, s.is_linked())
        s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
        self.assertEqual(True, s.is_linked())

    def test_wrong_id(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID+'a',
                self.CLOUDFS_SECRET)

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.InvalidRequest,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)


    def test_wrong_secret(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET+'a')

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.InvalidRequest,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

    def test_wrong_base(self):
        s = Session('a'+self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.assertEqual(False, s.is_linked())
        self.assertRaises(
            errors.AuthenticatedError,
            s.authenticate,
            self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

    def test_base_formatting(self):
        base_versions = [
            'http://' + self.CLOUDFS_BASE,
            'https://' + self.CLOUDFS_BASE,
            'http://www.' + self.CLOUDFS_BASE,
            'www.' + self.CLOUDFS_BASE
        ]

        for version in base_versions:
            s = Session(version,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)
            self.assertEqual(False, s.is_linked())
            s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
            self.assertEqual(True, s.is_linked())

    def test_create_user(self):
        # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
        def id_generator(size=6):
            return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.assertEqual(False, s.is_linked())
        username = id_generator()
        password = id_generator()
        self.assertRaises(
            errors.OperationNotAllowed,
            s.create_account,
            username, password
        )

        if self.ADMIN_ID != '' and self.ADMIN_SECRET != '':
            s.set_admin_credentials(self.ADMIN_ID, self.ADMIN_SECRET)
            user = s.create_account(username, password)
            self.assertEqual(False, s.is_linked())
            self.assertRaises(
                errors.SessionNotLinked,
                user.refresh
            )

            username2 = id_generator()
            user2 = s.create_account(username2, password, log_in_after_creation=True)
            self.assertEqual(True, s.is_linked())
            user2.refresh()

    def test_history(self):
        s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)

        history = s.get_history(start = -10)
        self.assertTrue(len(history) < 10)
        self.assertTrue(history[-1]['version'] < 10)


if __name__ == '__main__':

    unittest.main()
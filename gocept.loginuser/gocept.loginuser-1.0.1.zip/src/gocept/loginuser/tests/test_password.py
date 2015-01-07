import unittest


class PasswordHashingTest(unittest.TestCase):

    def setUp(self):
        import gocept.loginuser.password
        import gocept.testing.patch
        self.patch = gocept.testing.patch.Patches()
        self.patch.set(gocept.loginuser.password, 'WORK_FACTOR', 4)

    def tearDown(self):
        self.patch.reset()

    def test_verifying_passwords(self):
        import gocept.loginuser.password
        hashed = gocept.loginuser.password.hash('mypassword')
        self.assertTrue(gocept.loginuser.password.check(
            'mypassword', hashed))
        self.assertFalse(gocept.loginuser.password.check(
            'invalid', hashed))

    def test_hash_accepts_and_returns_unicode(self):
        import gocept.loginuser.password
        hashed = gocept.loginuser.password.hash(u'mypassword')
        self.assertIsInstance(hashed, unicode)

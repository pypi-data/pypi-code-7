from dcbase.tests.browser import BrowserTestCase
from dcbase.tests.browser.pages.profileEditPage import ProfileEditPage
from dcbase.tests.browser.pages.profilePage import ProfilePage


class TestProfilePage(BrowserTestCase):
    _pageClass = ProfilePage
    _requiresLogin = True

    def test_editProfileButtonGoesToProfileEditPage(self):
        self.page.clickProfileEdit()
        ProfileEditPage(self.browser)


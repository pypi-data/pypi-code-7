from dcbase.tests.browser.pages.pageObject import PageObject


class ProfilePage(PageObject):
    _urlPattern = '/accounts/profile/'
    _pageName = 'Profile'

    def clickProfileEdit(self):
        element = self.browser.find_element_by_id('edit-profile')
        element.click()


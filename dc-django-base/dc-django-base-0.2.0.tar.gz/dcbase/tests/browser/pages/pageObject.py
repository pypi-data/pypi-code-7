from urllib.parse import urlparse


class PageObject(object):
    _urlPattern = 'INVALID'
    _pageName = 'UNKNOWN PAGE NAME'

    def __init__(self, browser):
        self.browser = browser
        self._assertBrowserAtPageUrl()

    @classmethod
    def get(cls, browser, baseUrl, **urlFields):
        browser.get(baseUrl + cls._urlPattern.format(urlFields))
        return cls(browser, **urlFields)

    def _assertBrowserAtPageUrl(self):
        currentUrl = self.browser.current_url
        result = urlparse(currentUrl)
        if result.path != self._urlPattern:
            raise RuntimeError('Current browser page (%s) is not %s page (%s)' % (currentUrl, self._pageName, self._urlPattern))

    def hasElementWithId(self, elementId):
        element = self.getElementOrNoneById(elementId)
        return element is not None

    def hasSuccessAlert(self):
        return self._hasAlert('success')

    def hasErrorAlert(self):
        return self._hasAlert('danger')

    def _hasAlert(self, alertType):
        return len(self.browser.find_elements_by_class_name('alert-%s' % alertType)) is not 0

    def getElementOrNoneById(self, id):
        try:
            return self.browser.find_element_by_id(id)
        except:
            return None

    def getElementOrNoneByLinkText(self, text):
        try:
            return self.browser.find_element_by_link_text(text)
        except:
            return None


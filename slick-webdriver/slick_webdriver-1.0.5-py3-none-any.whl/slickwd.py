"""
"""

__author__ = 'jcorbett'

import logging
from enum import Enum
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
import time


class BrowserType(Enum):
    """
    This enum is to help identify browsers to launch.  The values are the desired capabilities.  All
    values are static properties on the BrowserType class.

    Example Use::

        from slickwd import Browser, BrowserType

        browser = Browser(BrowserType.CHROME)

    """
    CHROME = (DesiredCapabilities.CHROME, webdriver.Chrome)
    """
    Chrome Browser (you must download
    `chromedriver <https://sites.google.com/a/chromium.org/chromedriver/downloads>`_ separately and place in path)
    """
    FIREFOX = (DesiredCapabilities.FIREFOX, webdriver.Firefox)
    """Firefox Browser"""
    IE = (DesiredCapabilities.INTERNETEXPLORER, webdriver.Ie)
    """
    Internet Explorer Browser (you must download `internet explorer driver
    <https://code.google.com/p/selenium/wiki/InternetExplorerDriver>`_ separately and place it in your path)"""
    OPERA = (DesiredCapabilities.OPERA, webdriver.Opera)
    """Opera Browser"""
    SAFARI = (DesiredCapabilities.SAFARI, webdriver.Safari)
    """Safari Browser"""
    HTMLUNITWITHJS = (DesiredCapabilities.HTMLUNITWITHJS, None)
    """HTMLUnit with Javascript enabled, only for use with Remote"""
    IPHONE = (DesiredCapabilities.IPHONE, None)
    IPAD = (DesiredCapabilities.IPAD, None)
    ANDROID = (DesiredCapabilities.ANDROID, None)
    PHANTOMJS = (DesiredCapabilities.PHANTOMJS, webdriver.PhantomJS)
    """PhantomJS headless browser (must download separately, `phantomjs homepage <http://phantomjs.org/>`_)"""


class Find:
    """
    Use the class methods on this class to create instances, which are used by the WebElementLocator class
    to find elements in a browser.

    Example Usage::

        Search_Query_Text_Field = WebElementLocator("Search Box", Find.by_name("q"))

    This would create an instance of WebElementLocator called Search_Query_Text_Field that can be found
    on the page by looking for an element with the name property set to *q*.
    """

    def __init__(self, by, value):
        self.finders = [(by, value),]


    def describe(self):
        """Describe this finder in a plain english sort of way.  This allows for better logging.
        Example output would be "name q" for `Find.by_name("q")`."""
        return " or ".join([Find.describe_single_finder(finder[0], finder[1]) for finder in self.finders])

    @classmethod
    def describe_single_finder(cls, name, value):
        if name is By.ID:
            return "id \"{}\"".format(value)
        elif name is By.NAME:
            return "name \"{}\"".format(value)
        elif name is By.CLASS_NAME:
            return "class name \"{}\"".format(value)
        elif name is By.LINK_TEXT:
            return "link text \"{}\"".format(value)
        elif name is By.PARTIAL_LINK_TEXT:
            return "link text containing \"{}\"".format(value)
        elif name is By.CSS_SELECTOR:
            return "css selector \"{}\"".format(value)
        elif name is By.XPATH:
            return "xpath {}".format(value)
        elif name is By.TAG_NAME:
            return "tag name \"{}\"".format(value)

    def Or(self, finder):
        """
        You can _or_ multiple finders together by using the Or method.  An example would be::

            Search_Query_Text_Field = WebElementLocator("Search Box", Find.by_name("q").Or(Find.by_id("q")))

        If you use this to include multiple finders, note that it is not super precise.  The framework iterates over
        the list of finders, and the first one that returns an element wins.

        :param finder: Another finder to consider when looking for the element.
        :type finder: :class:`.Find`
        :return: This same instance of Find with the other finder included.
        :rtype: :class:`.Find`
        """
        self.finders.extend(finder.finders)
        return self

    @classmethod
    def by_id(cls, id_value):
        """
        Find a web element using the element's _id_ attribute.

        :param id_value: the id of the web element you are looking for
        :type id_value: str
        :return: an instance of Find that uses the id as the way to find the element.
        :rtype: :class:`.Find`
        """
        return Find(By.ID, id_value)

    @classmethod
    def by_name(cls, name_value):
        """
        Find a web element using the element's _name_ attribute.

        :param name_value: the value of the name attribute of the web element you are looking for
        :type name_value: str
        :return: an instance of Find that uses the name attribute as the way to find the element.
        :rtype: :class:`.Find`
        """
        return Find(By.NAME, name_value)

    @classmethod
    def by_class_name(cls, class_name_value):
        """
        Find a web element by looking for one that uses a particular css class name.

        :param class_name_value: the name of one of the css classes of the web element you are looking for
        :type class_name_value: str
        :return: an instance of Find that uses it's css classes as the way to find the element.
        :rtype: :class:`.Find`
        """
        return Find(By.CLASS_NAME, class_name_value)

    @classmethod
    def by_link_text(cls, link_text_value):
        """
        Find a web element (a link or <a> tag) using the element's exact link text.

        :param link_text_value: the value of the link's inner text
        :type link_text_value: str
        :return: an instance of Find that uses the link's text as the way to find the element.
        :rtype: :class:`.Find`
        """
        return Find(By.LINK_TEXT, link_text_value)

    @classmethod
    def by_partial_link_text(cls, partial_link_text_value):
        """
        Find a web element (a link or <a> tag) using part of the element's link text.

        :param partial_link_text_value: a subset of the value of the link's inner text
        :type partial_link_text_value: str
        :return: an instance of Find that uses part of the link's text as the way to find the element.
        :rtype: :class:`.Find`
        """
        return Find(By.PARTIAL_LINK_TEXT, partial_link_text_value)

    @classmethod
    def by_css_selector(cls, css_selector_value):
        """
        Find a web element by using a css selector

        :param css_selector_value: the css selector that will identify the element
        :type css_selector_value: str
        :return: an instance of Find that uses a css selector to find the element
        :rtype: :class:`.Find`
        """
        return Find(By.CSS_SELECTOR, css_selector_value)

    @classmethod
    def by_xpath(cls, xpath_value):
        """
        Find a web element by using a xpath.

        :param xpath_value: the xpath expression that will identify the element
        :type xpath_value: str
        :return: an instance of Find that uses an xpath expression to find the element
        :rtype: :class:`.Find`
        """
        return Find(By.XPATH, xpath_value)

    @classmethod
    def by_tag_name(cls, tag_name_value):
        """
        Find an element using it's tag name.  This is more useful when trying to find multiple elements.

        :param tag_name_value: the name of the html tag for the element or elements your are looking for
        :type tag_name_value: str
        :return: an instance of Find that looks for all elements on a page with a particular tag name
        :rtype: :class:`.Find`
        """
        return Find(By.TAG_NAME, tag_name_value)


# there is no doc because this is not intended to be used externally (not that it can't be)
class Timer:

    def __init__(self, length_in_seconds):
        self.start = time.time()
        self.end = self.start + length_in_seconds

    def is_past_timeout(self):
        return time.time() > self.end


class WebElementLocator:
    """
    A WebElementLocator represents information about an element you are trying to find.  It has a name field for
    nice logging, and a finder field (should be of type :class:`.Find`).

    See :doc:`locators`
    """

    def __init__(self, name, finder):
        # id=None, xpath=None, link_text=None, partial_link_text=None, name=None, href=None,
        # tag_name=None, class_name=None, css_selector=None):
        self.name = name
        self.finder = finder
        self.logger = logging.getLogger("slickwd.WebElementLocator")
        self.parent = None
        self.parent_initialized = False
        self.description = "{} found by {}".format(name, finder.describe())

    def get_page_name(self):
        if self.parent is not None:
            return self.parent.get_name()

    def find_all_elements_matching(self, wd_browser, log=True):
        """
        Find a list of elements that match a finder.  This method can be useful if you are
        :doc:`raw-webdriver` and need to select from and inspect a list of elements.

        There is no timeout because it will return an empty list if no matching elements are found.

        :param wd_browser: The raw selenium webdriver driver instance.
        :param log: Whether or not to log details of the look for the element (default is True)
        :type log: bool
        :return: list of matching elements
        :rtype: list of web element
        """
        retval = []
        if log:
            self.logger.debug("Looking for a list of elements matching {}".format(self.describe()))
        for finder in self.finder.finders:
            try:
                retval.extend(wd_browser.find_elements(finder[0], finder[1]))
            except WebDriverException:
                pass
        if log:
            self.logger.info("Found {} elements matching {}".format(len(retval), self.describe()))
        return retval

    def find_element_matching(self, wd_browser, timeout, log=True):
        """
        Find a single element matching the finder(s) that make up this locator before a timeout is reached.
        This method is used internally by the framework when you call any action on a WebElementLocator, however
        like is mentioned in :doc:`raw-webdriver` you can use this method to help you get the raw webelements from
        webdriver for your own use.

        :param wd_browser: The selenium driver (webdriver) instance to use.
        :param timeout: the max time (in seconds) to wait before giving up on finding the element
        :type timeout: int or float (use float for sub-second precision)
        :param log: Whether or not to log details of the look for the element (default is True)
        :type log: bool
        :return: a raw webdriver webelement type on success, None on failure
        """
        if timeout == 0:
            if log:
                self.logger.debug("Attempting 1 time to find element {} .".format(self.describe()))
            for finder in self.finder.finders:
                try:
                    return wd_browser.find_element(finder[0], finder[1])
                except WebDriverException:
                    pass
            else:
                if log:
                    self.logger.warn("Unable to find element {}".format(self.describe()))
                return None
        else:
            retval = None
            timer = Timer(timeout)
            if log:
                self.logger.debug("Waiting for up to {:.2f} seconds for element {} to be available.".format(float(timeout), self.describe()))
            while not timer.is_past_timeout():
                for finder in self.finder.finders:
                    try:
                        retval =  wd_browser.find_element(finder[0], finder[1])
                    except WebDriverException:
                        pass
                    if retval is not None:
                        if log:
                            self.logger.info("Found element {} using locator property {} after {:.2f} seconds.".format(self.name, Find.describe_single_finder(finder[0], finder[1]), time.time() - timer.start))
                        return retval
                time.sleep(.25)

    def describe(self):
        """
        Describe the current locator in plain english.  Used for logging.

        :return: description of element locator including name and how it is looking for it
        :rtype: str
        """
        if self.parent is not None and self.parent_initialized is False:
            self.description = "{} on page {} found by {}".format(self.name, self.parent.get_name(), self.finder.describe())
            self.parent_initialized = True
        return self.description

class Browser:
    """
    The Browser is the primary interface you have to automate a browser.  An instance of Browser has the same
    methods no matter which browser it is you launch.  It also abstracts away the creation of remote browser
    instances when using `Selenium Grid <https://code.google.com/p/selenium/wiki/Grid2>`_ or `Selenium Server
    <http://selenium-python.readthedocs.org/en/latest/installation.html#downloading-selenium-server>`_.

    Most actions that the Browser has takes an argument called locator, which should be an instance of
    :class:`.WebElementLocator`.  These are normally arranged into Page classes to make them reusable
    by multiple tests / functions.  See :doc:`page-classes`.

    To create an instance of Browser, provide the browser type you would like, and the remote_url (if any)::

        from slickwd import Browser, BrowserType

        browser = Browser(BrowserType.PHANTOMJS)
        browser.go_to("http://www.google.com")

    For more examples, see :doc:`examples`.
    """

    def __init__(self, browser_type, remote_url=None, default_timeout=30):
        """
        Create a new browser session.  The only required parameter *browser_type* can be
        an instance of the *BrowserType* enum, a dictionary (like those from webdriver's desired_capabilities),
        or a string identifying the name of the browser (must correspond to a name in the *BrowserType* enum).

        If you use a remote_url, it should point to a selenium remote server.
        """
        self.default_timeout = default_timeout

        # tame the huge logs from webdriver
        wdlogger = logging.getLogger('selenium.webdriver')
        wdlogger.setLevel(logging.WARNING)

        self.logger = logging.getLogger("slickwd.Browser")
        browser_name = browser_type
        if isinstance(browser_type, BrowserType):
            browser_name = browser_type.name
        elif isinstance(browser_type, dict) and 'browserName' in browser_type:
            browser_name = browser_type[browser_name]
        self.logger.debug("New browser instance requested with browser_type={} and remote_url={}".format(repr(browser_name), repr(remote_url)))
        if isinstance(browser_type, str):
            try:
                browser_type = BrowserType[browser_type.upper()]
            except:
                raise WebDriverException("Invalid browser name: \"{}\"".format(browser_type))

        if remote_url is None:
            if isinstance(browser_type, dict) and 'browserName' in browser_type:
                browser_name = browser_type['browserName']
                if browser_name == 'internet explorer':
                    browser_name = 'ie'
                if browser_name == 'htmlunit':
                    browser_name = 'htmlunitwithjs'
                try:
                    browser_type = BrowserType[browser_name.upper()]
                except:
                    raise WebDriverException("Invalid browser: \"{}\"".format(browser_name))
            if not isinstance(browser_type, BrowserType):
                raise WebDriverException("Unable to create browser of type \"{}\"".format(repr(browser_type)))
            if browser_type.value[1] is None:
                raise WebDriverException("Browser of type \"{}\" can only be launched remotely, which means you must provide a remote_url.".format(browser_type.name))

            self.remote_url = remote_url
            self.browser_type = browser_type
            self.logger.info("Creating a new browser (locally connected) of type {}".format(browser_type.name.lower()))
            self.wd_instance = browser_type.value[1]()
        else:
            if isinstance(browser_type, BrowserType):
                browser_type = browser_type.value[0]

            if not isinstance(browser_type, dict):
                raise WebDriverException("Unable to create a browser of type \"{}\", when using remote_url browser_type should be either an instance of BrowserType or a dictionary containing desired capabilities.".format(repr(browser_type)))

            self.remote_url = remote_url
            self.browser_type = browser_type
            self.logger.info("Creating a new browser (through remote connection \"{}\") with desired capabilities of {}".format(remote_url, repr(browser_type)))
            self.wd_instance = webdriver.Remote(remote_url, browser_type)

    def quit(self, log=True):
        """
        Close the browser and quit the current session

        :return: this instance for chaining of methods
        :rtype: :class:`.Browser`
        """
        if log:
            self.logger.info("Calling quit on browser instance.")
        self.wd_instance.quit()
        return self

    def go_to(self, url, log=True):
        """Navigate the browser to the url provided"""
        if log:
            self.logger.debug("Navigating to url {}.".format(repr(url)))
        self.wd_instance.get(url)
        return self

    def wait_for_page(self, page, timeout=None, log=True):
        """
        Wait for a page class (container) to be present.
        This will cause that the page's *is_current_page* method to be called until it returns true or a timeout
        is reached.

        :param page: The page class (container) to wait for it's is_current_page to return True
        :type page: :class:`.Container`
        :param timeout: the max time (in seconds) to wait before giving up on the page existing
        :type timeout: int or float (use float for sub-second precision)
        :param log: Should the activities of this method be logged, default is True
        :type log: bool
        :return: this instance for chaining of methods
        :rtype: :class:`.Browser`
        """
        # create an instance of the page
        page_instance = None
        if isinstance(page, Container):
            page_instance = page
        else:
            page_instance = page()
        assert isinstance(page_instance, Container)

        if timeout is None:
            timeout = self.default_timeout

        if log:
            self.logger.debug("Waiting for up to {:.2f} seconds for page {} to be the current page.".format(float(timeout), page_instance.get_name()))

        timer = Timer(timeout)
        while not timer.is_past_timeout():
            if page_instance.is_current_page(self):
                break
            time.sleep(0.25) # sleep a quarter of a second
        else:
            # The timer.is_past_timeout() returned true and that kicked us out of the loop
            if log:
                self.logger.warn("Waited {:.2f} seconds for page {} to exist and it never returned true from is_current_page.".format(float(timeout), page_instance.get_name()))
            raise WebDriverException("Waited {:.2f} seconds for page {} to exist and it never returned true from is_current_page.".format(float(timeout), page_instance.get_name()))
        self.logger.debug("Found page {} after {:.2f} seconds.".format(page_instance.get_name(), time.time() - timer.start))
        return self

    def exists(self, locator, timeout=None, log=True):
        """
        Check to see if an element exists on a page.  You can control how long to wait, and if the method should do
        any logging.  If you specify 0 for the timeout, the framework will only look for the element once.

        :param locator: the locator to look for (usually defined on a Page class)
        :type locator: :class:`.WebElementLocator`
        :param timeout: The amount of time (in seconds) to look before returning False
        :type timeout: int or float
        :param log: Whether or not to log details of the look for the element (default is True)
        :type log: bool
        :return: True if an element was found in the time specified
        :rtype: bool
        """
        if timeout is None:
            timeout = self.default_timeout
        return locator.find_element_matching(self.wd_instance, timeout, log) is not None

    def click(self, locator, timeout=None, log=True):
        """
        Click on an element using the mouse.

        :param locator: the locator that specifies which element to click on (usually defined on a Page class)
        :type locator: :class:`.WebElementLocator`
        :param timeout: The amount of time (in seconds) to look before throwing a not found exception
        :type timeout: int or float (float for sub-second precision)
        :param log: Whether or not to log details of the look for the element (default is True)
        :type log: bool
        :return: The reference to this Browser instance.
        :rtype: :class:`.Browser`
        """
        if timeout is None:
            timeout = self.default_timeout
        element = locator.find_element_matching(self.wd_instance, timeout, log)
        if element is None:
            raise WebDriverException("Unable to find element {} after waiting for {:.2f} seconds".format(locator.describe(), float(timeout)))
        if log:
            self.logger.debug("Clicking on element {}".format(locator.describe()))
        element.click()
        return self

    def click_and_type(self, locator, keys, timeout=None, log=True):
        """
        Click on an element using the mouse, then send keys to it.  Mostly used for input elements of type text.

        :param locator: the locator that specifies which element to click on and type in (usually defined on a Page class)
        :type locator: :class:`.WebElementLocator`
        :param timeout: The amount of time (in seconds) to look before throwing a not found exception
        :type timeout: int or float (float for sub-second precision)
        :param log: Whether or not to log details of the look for the element (default is True)
        :type log: bool
        :return: The reference to this Browser instance.
        :rtype: :class:`.Browser`
        """
        if timeout is None:
            timeout = self.default_timeout
        element = locator.find_element_matching(self.wd_instance, timeout, log)
        if element is None:
            raise WebDriverException("Unable to find element {} after waiting for {:.2f} seconds".format(locator.describe(), float(timeout)))
        if log:
            self.logger.debug("Clicking on element {}".format(locator.describe()))
        element.click()
        if log:
            self.logger.debug("Typing \"{}\" into element {}".format(keys, locator.describe()))
        element.send_keys(keys)
        return self

    def get_page_text(self):
        """
        Get the text from the current web page.  This tries to get the value of the "text" attribute of the html
        root element on the page.

        :return: the text of the current page
        :rtype: str
        """
        element = self.wd_instance.find_element_by_tag_name("html")
        if element is not None:
            return element.text

    def get_text(self, locator, timeout=None, log=True):
        """
        Get the text of an element on the page.

        :param locator: the locator that specifies which element to get the text of
        :type locator: :class:`.WebElementLocator`
        :param timeout: The amount of time (in seconds) to look before throwing a not found exception
        :type timeout: int or float (float for sub-second precision)
        :param log: Whether or not to log details of the look for the element (default is True)
        :type log: bool
        :return: the text of the element on success, exception raised on inability to find the element
        :rtype: str
        """
        if timeout is None:
            timeout = self.default_timeout
        element = locator.find_element_matching(self.wd_instance, timeout, log)
        if element is None:
            raise WebDriverException("Unable to find element {} after waiting for {:.2f} seconds".format(locator.describe(), float(timeout)))
        text = element.text
        if log:
            self.logger.debug("Found element {}, returning text: {}".format(locator.describe(), text))
        return text

    def get_attribute_value(self, locator, attribute_name, timeout=None, log=True):
        """
        Get the value of an html element's attribute.

        :param locator: the locator that specifies which element to get the attribute value of
        :type locator: :class:`.WebElementLocator`
        :param attribute_name: the name of the attribute to get
        :type attribute_name: str
        :param timeout: The amount of time (in seconds) to look before throwing a not found exception
        :type timeout: int or float (float for sub-second precision)
        :param log: Whether or not to log details of the look for the element (default is True)
        :type log: bool
        :return: the text of the element on success, exception raised on inability to find the element
        :rtype: str
        """
        if timeout is None:
            timeout = self.default_timeout
        element = locator.find_element_matching(self.wd_instance, timeout, log)
        if element is None:
            raise WebDriverException("Unable to find element {} after waiting for {:.2f} seconds".format(locator.describe(), float(timeout)))
        value = element.get_attribute(attribute_name)
        if log:
            self.logger.debug("Found element {}, attribute {} has value: {}".format(locator.describe(), attribute_name, value))
        return value


class Container:
    """
    A generic container for structuring multiple *WebElementLocator* into groupings that help programmers find the right
    shared definition.
    """

    def get_name(self):
        if hasattr(self, "parent") and hasattr(self, "container_name") and self.parent is not None:
            return "{}.{}".format(self.parent.get_name(), self.container_name)
        elif hasattr(self, "container_name"):
            return self.container_name
        else:
            name = self.__class__.__name__
            if name.endswith("Page"):
                name = name[:-4]
            return name

    def is_current_page(self, browser):
        raise NotImplementedError("is_current_page was not implemented on class: {}".format(self.__class__.__name__))

    def __setattr__(self, key, value):
        # this magic is for naming and setting of parent -> child relationships
        if key != "parent":
            if isinstance(value, Container):
                value.parent = self
                value.container_name = key
            if isinstance(value, WebElementLocator):
                value.parent = self
        return super(Container, self).__setattr__(key, value)




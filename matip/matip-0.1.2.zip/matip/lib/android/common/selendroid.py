#!/user/bin/env python
# -*- coding: utf-8 -*-

from matip.lib.android.server.selendroid import SelendroidServer
from matip.lib.android.common.switch_to import SwitchTo
from matip.lib.android.common.touch_actions import TouchActions
from matip.lib.android.common import proxy
from matip.lib.android.common.mobilewebelement import MobileWebElement
from matip.lib.android.common.by import By
from matip.lib.android.common.command import Command


class Selendroid(object):
    """
    Attributes:
    #- platformName eg:Android
    - app
    - device
    - model: native or hybrid
    """
    def __init__(self,desired_capabilities):
        self.server = SelendroidServer(desired_capabilities)
        self.session_id = self.server.start()
        self._switch_to = SwitchTo(self)
        self._actions = TouchActions(self)
            

    def _wrap_value(self, value):
        if isinstance(value, dict):
            converted = {}
            for key, val in value.items():
                converted[key] = self._wrap_value(val)
            return converted
        elif isinstance(value, MobileWebElement):
            return {'ELEMENT': value.id}
        elif isinstance(value, list):
            return list(self._wrap_value(item) for item in value)
        else:
            return value

    def create_web_element(self, element_id):
        """
        Creates a web element with the specified element_id.
        """
        return MobileWebElement(self, element_id)

    def _unwrap_value(self, value):
        if isinstance(value, dict) and 'ELEMENT' in value:
            return self.create_web_element(value['ELEMENT'])
        elif isinstance(value, list):
            return list(self._unwrap_value(item) for item in value)
        else:
            return value
        
    def check_response(self, response):
        status = response['status']
        if status == 0:
            return
        value = response['value']
        if isinstance(value, basestring):
            raise Exception(value)
        else:
            raise Exception(str(value))
        
    def execute(self, driver_command, params=None):
        """
        Sends a command to be executed by a command.CommandExecutor.

        :Args:
         - driver_command: The name of the command to execute as a string.
         - params: A dictionary of named parameters to send with the command.

        :Returns:
          The command's JSON response loaded into a dictionary object.
        """
        if self.session_id is not None:
            if not params:
                params = {'sessionId': self.session_id}
            elif 'sessionId' not in params:
                params['sessionId'] = self.session_id

        params = self._wrap_value(params)
        response = proxy.execute(driver_command, params)
        if response:
            self.check_response(response)
            response['value'] = self._unwrap_value(
                response.get('value', None))
            return response
        # If the server doesn't send a response, assume the command was
        # a success
        return {'success': 0, 'value': None, 'sessionId': self.session_id}


    @property
    def contexts(self):
        """
        Returns the contexts within the current session.

        :Usage:
            driver.contexts
        """
        return self.execute(Command.GET_CONTEXTS)['value']

    @property
    def current_context(self):
        """
        Returns the current context of the current session.

        :Usage:
            driver.current_context
        """
        return self.execute(Command.GET_CURRENT_CONTEXT)['value']

    @property
    def context(self):
        """
        Returns the current context of the current session.

        :Usage:
            driver.context
        """
        return self.current_context

    def open_url(self, url):
        """
        Loads a web page in the current browser session.
        """
        self.execute(Command.OPEN_URL, {'url': url})

    @property
    def title(self):
        """Returns the title of the current page.

        :Usage:
            driver.title
        """
        resp = self.execute(Command.GET_TITLE)
        return resp['value'] if resp['value'] is not None else ""

    def find_element(self, by=By.ID, value=None):
        """
        'Private' method used by the find_element_by_* methods.

        :Usage:
            Use the corresponding find_element_by_* instead of this.

        :rtype: WebElement
        """
        if not By.is_valid(by) or not isinstance(value, str):
            msg = "Invalid locator values passed in"
            raise Exception(msg)
        
        return self.execute(Command.FIND_ELEMENT,
                             {'using': by, 'value': value})['value']

    def find_elements(self, by=By.ID, value=None):
        """
        'Private' method used by the find_elements_by_* methods.

        :Usage:
            Use the corresponding find_elements_by_* instead of this.

        :rtype: list of WebElement
        """
        if not By.is_valid(by) or not isinstance(value, str):
            msg = "Invalid locator values passed in"
            raise Exception(msg)

        return self.execute(Command.FIND_ELEMENTS,
                             {'using': by, 'value': value})['value']


    def find_element_by_id(self, id_):
        """Finds an element by id.

        :Args:
         - id\_ - The id of the element to be found.

        :Usage:
            driver.find_element_by_id('foo')
        """
        return self.find_element(by=By.ID, value=id_)

    def find_elements_by_id(self, id_):
        """
        Finds multiple elements by id.

        :Args:
         - id\_ - The id of the elements to be found.

        :Usage:
            driver.find_element_by_id('foo')
        """
        return self.find_elements(by=By.ID, value=id_)

    def find_element_by_xpath(self, xpath):
        """
        Finds an element by xpath.

        :Args:
         - xpath - The xpath locator of the element to find.

        :Usage:
            driver.find_element_by_xpath('//div/td[1]')
        """
        return self.find_element(by=By.XPATH, value=xpath)

    def find_elements_by_xpath(self, xpath):
        """
        Finds multiple elements by xpath.

        :Args:
         - xpath - The xpath locator of the elements to be found.

        :Usage:
            driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """
        return self.find_elements(by=By.XPATH, value=xpath)

    def find_element_by_link_text(self, link_text):
        """
        Finds an element by link text.

        :Args:
         - link_text: The text of the element to be found.

        :Usage:
            driver.find_element_by_link_text('Sign In')
        """
        return self.find_element(by=By.LINK_TEXT, value=link_text)

    def find_elements_by_link_text(self, text):
        """
        Finds elements by link text.

        :Args:
         - link_text: The text of the elements to be found.

        :Usage:
            driver.find_elements_by_link_text('Sign In')
        """
        return self.find_elements(by=By.LINK_TEXT, value=text)

    def find_element_by_partial_link_text(self, link_text):
        """
        Finds an element by a partial match of its link text.

        :Args:
         - link_text: The text of the element to partially match on.

        :Usage:
            driver.find_element_by_partial_link_text('Sign')
        """
        return self.find_element(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_elements_by_partial_link_text(self, link_text):
        """
        Finds elements by a partial match of their link text.

        :Args:
         - link_text: The text of the element to partial match on.

        :Usage:
            driver.find_element_by_partial_link_text('Sign')
        """
        return self.find_elements(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_element_by_name(self, name):
        """
        Finds an element by name.

        :Args:
         - name: The name of the element to find.

        :Usage:
            driver.find_element_by_name('foo')
        """
        return self.find_element(by=By.NAME, value=name)

    def find_elements_by_name(self, name):
        """
        Finds elements by name.

        :Args:
         - name: The name of the elements to find.

        :Usage:
            driver.find_elements_by_name('foo')
        """
        return self.find_elements(by=By.NAME, value=name)

    def find_element_by_tag_name(self, name):
        """
        Finds an element by tag name.

        :Args:
         - name: The tag name of the element to find.

        :Usage:
            driver.find_element_by_tag_name('foo')
        """
        return self.find_element(by=By.TAG_NAME, value=name)

    def find_elements_by_tag_name(self, name):
        """
        Finds elements by tag name.

        :Args:
         - name: The tag name the use when finding elements.

        :Usage:
            driver.find_elements_by_tag_name('foo')
        """
        return self.find_elements(by=By.TAG_NAME, value=name)

    def find_element_by_class_name(self, name):
        """
        Finds an element by class name.

        :Args:
         - name: The class name of the element to find.

        :Usage:
            driver.find_element_by_class_name('foo')
        """
        return self.find_element(by=By.CLASS_NAME, value=name)

    def find_elements_by_class_name(self, name):
        """
        Finds elements by class name.

        :Args:
         - name: The class name of the elements to find.

        :Usage:
            driver.find_elements_by_class_name('foo')
        """
        return self.find_elements(by=By.CLASS_NAME, value=name)

    def find_element_by_css_selector(self, css_selector):
        """
        Finds an element by css selector.

        :Args:
         - css_selector: The css selector to use when finding elements.

        :Usage:
            driver.find_element_by_css_selector('#foo')
        """
        return self.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def find_elements_by_css_selector(self, css_selector):
        """
        Finds elements by css selector.

        :Args:
         - css_selector: The css selector to use when finding elements.

        :Usage:
            driver.find_elements_by_css_selector('.foo')
        """
        return self.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def execute_script(self, script, *args):
        """
        Synchronously Executes JavaScript in the current window/frame.

        :Args:
         - script: The JavaScript to execute.
         - \*args: Any applicable arguments for your JavaScript.

        :Usage:
            driver.execute_script('document.title')
        """
        converted_args = list(args)
        return self.execute(Command.EXECUTE_SCRIPT,
            {'script': script, 'args':converted_args})['value']

    def execute_async_script(self, script, *args):
        """
        Asynchronously Executes JavaScript in the current window/frame.

        :Args:
         - script: The JavaScript to execute.
         - \*args: Any applicable arguments for your JavaScript.

        :Usage:
            driver.execute_async_script('document.title')
        """
        converted_args = list(args)
        return self.execute(Command.EXECUTE_ASYNC_SCRIPT,
            {'script': script, 'args':converted_args})['value']

    @property
    def current_url(self):
        """
        Gets the URL of the current page.

        :Usage:
            driver.current_url
        """
        return self.execute(Command.GET_CURRENT_URL)['value']

    @property
    def page_source(self):
        """
        Gets the source of the current page.

        :Usage:
            driver.page_source
        """
        return self.execute(Command.GET_PAGE_SOURCE)['value']

    def quit(self):
        """
        Quits the driver and closes every associated window.

        :Usage:
            driver.selentroid.quit()
        """
        try:
            self.execute(Command.QUIT)
        except:
            pass
    
    @property
    def current_window_handle(self):
        """
        Returns the handle of the current window.

        :Usage:
            driver.current_window_handle
        """
        return self.execute(Command.GET_CURRENT_WINDOW_HANDLE)['value']

    @property
    def window_handles(self):
        """
        Returns the handles of all windows within the current session.

        :Usage:
            driver.window_handles
        """
        return self.execute(Command.GET_WINDOW_HANDLES)['value']

    @property
    def switch_to(self):
        return self._switch_to

    @property
    def actions(self):
        return self._actions
    
    #Navigation
    def back(self):
        """
        Goes one step backward in the browser history.

        :Usage:
            driver.back()
        """
        self.execute(Command.GO_BACK)

    def forward(self):
        """
        Goes one step forward in the browser history.

        :Usage:
            driver.forward()
        """
        self.execute(Command.GO_FORWARD)

    def refresh(self):
        """
        Refreshes the current page.

        :Usage:
            driver.refresh()
        """
        self.execute(Command.REFRESH)

    # Options
    def get_cookies(self):
        """
        Returns a set of dictionaries, corresponding to cookies visible in the current session.

        :Usage:
            driver.get_cookies()
        """
        return self.execute(Command.GET_ALL_COOKIES)['value']

    def get_cookie(self, name):
        """
        Get a single cookie by name. Returns the cookie if found, None if not.

        :Usage:
            driver.get_cookie('my_cookie')
        """
        cookies = self.get_cookies()
        for cookie in cookies:
            if cookie['name'] == name:
                return cookie
        return None

    def delete_cookie(self, name):
        """
        Deletes a single cookie with the given name.

        :Usage:
            driver.delete_cookie('my_cookie')
        """
        self.execute(Command.DELETE_COOKIE, {'name': name})

    def delete_all_cookies(self):
        """
        Delete all cookies in the scope of the session.

        :Usage:
            driver.delete_all_cookies()
        """
        self.execute(Command.DELETE_ALL_COOKIES)

    def add_cookie(self, cookie_dict):
        """
        Adds a cookie to your current session.

        :Args:
         - cookie_dict: A dictionary object, with required keys - "name" and "value";
            optional keys - "path", "domain", "secure", "expiry"

        Usage:
            driver.add_cookie({'name' : 'foo', 'value' : 'bar'})
            driver.add_cookie({'name' : 'foo', 'value' : 'bar', 'path' : '/'})
            driver.add_cookie({'name' : 'foo', 'value' : 'bar', 'path' : '/', 'secure':True})

        """
        self.execute(Command.ADD_COOKIE, {'cookie': cookie_dict})

    # Timeouts
    def implicitly_wait(self, time_to_wait):
        """
        Sets a sticky timeout to implicitly wait for an element to be found,
           or a command to complete. This method only needs to be called one
           time per session. To set the timeout for calls to
           execute_async_script, see set_script_timeout.

        :Args:
         - time_to_wait: Amount of time to wait (in seconds)

        :Usage:
            driver.implicitly_wait(30)
        """
        self.execute(Command.IMPLICIT_WAIT, {'ms': float(time_to_wait) * 1000})

    def set_script_timeout(self, time_to_wait):
        """
        Set the amount of time that the script should wait during an
           execute_async_script call before throwing an error.

        :Args:
         - time_to_wait: The amount of time to wait (in seconds)

        :Usage:
            driver.set_script_timeout(30)
        """
        self.execute(Command.SET_SCRIPT_TIMEOUT,
            {'ms': float(time_to_wait) * 1000})

    def set_page_load_timeout(self, time_to_wait):
        """
        Set the amount of time to wait for a page load to complete
           before throwing an error.

        :Args:
         - time_to_wait: The amount of time to wait

        :Usage:
            driver.set_page_load_timeout(30)
        """
        self.execute(Command.SET_TIMEOUTS,
            {'ms': float(time_to_wait) * 1000, 'type':'page load'})

    @property
    def orientation(self):
        """
        Gets the current orientation of the device

        :Usage:
            orientation = driver.orientation
        """
        return self.execute(Command.GET_SCREEN_ORIENTATION)['value']

    @orientation.setter
    def orientation(self, value):
        """
        Sets the current orientation of the device

        :Args:
         - value: orientation to set it to.

       :Usage:
            driver.orientation = 'landscape'
        """
        allowed_values = ['LANDSCAPE', 'PORTRAIT']
        if value.upper() in allowed_values:
            self.execute(Command.SET_SCREEN_ORIENTATION, {'orientation': value})
        else:
            msg = "You can only set the orientation to 'LANDSCAPE' and 'PORTRAIT'"
            raise WebDriverException(msg)

    @property
    def adb_actions(self):
        return self._adb_actions

    

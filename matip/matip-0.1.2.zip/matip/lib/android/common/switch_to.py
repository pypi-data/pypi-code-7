#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .command import Command
from .alert import Alert

class SwitchTo(object):
    def __init__(self,driver):
        self._driver = driver
        
    @property
    def alert(self):
        """
        Switches focus to an alert on the page.

        :Usage:
            alert = driver.switch_to.alert
        """
        return Alert(self._driver)

    def default_content(self):
        """
        Switch focus to the default frame.

        :Usage:
            driver.switch_to.default_content()
        """
        self._driver.execute(Command.SWITCH_TO_FRAME, {'id': None})

    def frame(self,frame_reference):
        """
        Switches focus to the specified frame, by index, name, or webelement.

        :Args:
         - frame_reference: The name of the window to switch to, an integer representing the index,
                            or a webelement that is an (i)frame to switch to.

        :Usage:
            driver.switch_to.frame('frame_name')
            driver.switch_to.frame(1)
            driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])
        """
        self._driver.execute(Command.SWITCH_TO_FRAME, {'id': frame_reference})

    def window(self, window_name):
        """
        Switches focus to the specified window.

        :Args:
         - window_name: The name or window handle of the window to switch to.

        :Usage:
            driver.switch_to.window('main')
        """
        self._driver.execute(Command.SWITCH_TO_WINDOW, {'name': window_name})

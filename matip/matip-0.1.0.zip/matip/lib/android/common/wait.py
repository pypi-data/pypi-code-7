#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

TIMEOUT = 5
INTERVAL = 0.5    #How long to sleep inbetween calls to the method

class Wait(object):

    def __init__(self,driver,timeout,interval=INTERVAL):
        """
        takes a driver instance and tiimeout in seconds.

        :Args:
         - driver - Instance of driver
         - timeout - Number of seconds before timeing out
         - poll_frequency - sleep interval between calls
           By default, it is -.5 second

        Example:
          from matip.lib.android.common.wait import Wait
          - hybrid
            element = Wait(driver,10).until(lambda x: x.find_element_by_id("someId"))
            is_disappeared = Wait(driver,30,1).until_not(lambda x: x.find_element_by_id("someId")).exists()
          - native
            element = Wait(driver,10).until(lambda x: x.find_element(class_name="ClassName"))
            is_disappeared = Wait(driver,30,1).until_not(lambda x: x.find_element(class_name="ClassName")).exists()
        """
        self._driver = driver
        self._timeout = timeout
        self._interval = interval
        if self._timeout == 0:
            self._timeout = TIMEOUT
        if self._interval == 0:
            self._interval = INTERVAL
        print self._timeout
        print self._interval
        
    def until(self,method,message=''):
        """
        Calls the method provided with the driver as an argument until the
        return value is not False
        """
        end_time = time.time() + self._timeout
        while(True):
            try:
                value = method(self._driver)
                if value.exists():
                    return value
            except:
                pass
            time.sleep(self._interval)
            if time.time() > end_time:
                break
        if message:
            msg = message
        else:
            msg = "timed out after %s seconds" % self._timeout
        raise Exception(msg)


    def until_not(self,method,message=""):
        """
        Calls the method provided with the driver as an argument until the
        return value is False
        """
        end_time = time.time() + self._timeout
        while(True):
            try:
                value = method(delf._driver)
                if not value:
                    return value
            except:
                pass
            time.sleep(self._poll)
            if time.time() > end_time:
                break
        if message:
            msg = message
        else:
            msg = "timed out after %s seconds" % self._timeout
        raise Exception(msg)


        

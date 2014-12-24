#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from adb_actions import AdbActions
class MobileElement(object):
    def __init__(self,element_object):
        self.element_object = element_object
        self.actions = AdbActions()

    def exists(self):
        """
        Whether the element would be exists
        """
        element = self.length()
        if self.element_object != []:
            return True
        else:
            return False

    def length(self):
        return len(self.element_object)

    def getList(self):
        new_elem = []
        for i in range(self.length()):
            res = self.element_objext[i:i+1]
            res.append(1)
            new_elem.append(MobileElement(res))
        return new_elem

    def items(self):
        self._assertExists()
        return self.element_object.items()
        
    @property
    def text(self):
        """
        Get the text of the element
        """
        return self._getValue("text")

    @property
    def id(self):
        """
        Get the resource-id of the element
        """
        return self._getValue("resource-id")

    @property
    def className(self):
        """
        Get the class name of the element
        """
        return self._getValue("class")

    @property
    def package(self):
        """
        Get the package of the element
        """
        return self._getValue("package")

    @property
    def desc(self):
        """
        Get the content-desc of the element
        """
        return self._getValue("content-desc")

    @property
    def checkable(self):
        """
        Get the checkable of the element
        """
        if self._getValue("checkable").lower() == "true":
            return True
        else:
            return False

    @property
    def checked(self):
        """
        Whether the element is checked
        """
        if self._getValue("checked").lower() == "true":
            return True
        else:
            return False

    @property
    def clickable(self):
        """
        Get the clickable of the element
        """
        if self._getValue("clickable").lower() == "true":
            return True
        else:
            return False

    @property
    def enabled(self):
        """
        Whether the element is enabled
        """
        if self._getValue("enabled").lower() == "true":
            return True
        else:
            return False

    @property
    def focusable(self):
        """
        Get the focusable of the element
        """
        if self._getValue("focusable").lower() == "true":
            return True
        else:
            return False

    @property
    def focused(self):
        """
        Whether the element is focused
        """
        if self._getValue("focused").lower() == "true":
            return True
        else:
            return False

    @property
    def scrollable(self):
        """
        Get the scrollable of the element
        """
        if self._getValue("scrollable").lower() == "true":
            return True
        else:
            return False

    @property
    def longClickable(self):
        """
        Get the long-clickable of the element
        """
        if self._getValue("long-clickable").lower() == "true":
            return True
        else:
            return False

    @property
    def password(self):
        """
        Get the password of the element
        """
        if self._getValue("password").lower() == "true":
            return True
        else:
            return False

    @property
    def selected(self):
        """
        Whether the element is selected
        """
        if self._getValue("selected").lower() == "true":
            return True
        else:
            return False

    @property
    def bounds(self):
        """
        Get the bounds of the element
        """
        bound = self._getValue("bounds")
        pattern = re.compile(r"\d+")
        coord = pattern.findall(bound)
        return coord

    def tap(self):
        """
        Click the element
        """
        xcoord,ycoord = self._getCoord()
        self.actions.tap(xcoord,ycoord)

    def swipeTo(self,obj=None,xcoord=None,ycoord=None):
        """
        Swipe the element
        """
        xstart,ystart = self._getCoord()
        if obj:
            xend,yend = self._getCoord(obj)
        elif x and y:
            xend = x
            yend = y
        else:
            msg = "Invalid argument"
            raise Exception(msg)
        self.actions.swipe(xstart,ystart,xend,yend)

    def swipeToLeft(self):
        """
        Swipe the element to left
        """
        xstart,ystart = self._getCoord()
        yend = ystart
        x,y = self.actions.assertRatio(0.1,0.5)
        xend = x
        self.swipeTo(xcoord=xend,ycoord=yend)

    def swipeToRight(self):
        """
        Swipe the element to right
        """
        xstart,ystart = self._getCoord()
        yend = ystart
        x,y = self.actions.assertRatio(0.9,0.5)
        xend = x
        self.swipeTo(xcoord=xend,ycoord=yend)

    def swipeToUp(self):
        """
        Swipe the element to up
        """
        xstart,ystart = self._getCoord()
        xend = xstart
        x,y = self.actions.assertRatio(0.5,0.1)
        yend = y
        self.swipeTo(xcoord=xend,ycoord=yend)

    def swipeToDown(self):
        """
        Swipe the element to Down
        """
        xstart,ystart = self._getCoord()
        xend = xstart
        x,y = self.actions.assertRatio(0.5,0.9)
        yend = y
        self.swipeTo(xcoord=xend,ycoord=yend)

    def sendText(self,text):
        """
        simulates typing into the element

        Does not support Chinese
        """
        self.tap()
        self.actions.sendText(text)
        
    def keyevent(self,keycode):
        self.actions.keyevent(keycode)
        
    def _assertExists(self):
        if not self.exists():
            msg = "unable to locate element"
            raise Exception(msg)

    def _getValue(self,key):
        self._assertExists()
        return self.element_object.get(key)
        
    def _getCoord(self,obj=None):
        if obj:
            coord = obj.bounds
        else:
            coord = self.bounds
        return self._getCenterCoord(coord)

    def _getCenterCoord(self,arr):
        xcoord = (int(arr[2]) - int(arr[0])) / 2.0 + int(arr[0])
        ycoord = (int(arr[3]) - int(arr[1])) / 2.0 + int(arr[1])
        return (xcoord,ycoord)

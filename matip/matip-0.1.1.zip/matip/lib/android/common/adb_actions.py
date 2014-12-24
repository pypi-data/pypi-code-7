#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import adb
from keys import Keys

class AdbActions(object):
    
    def keyevent(self,keycode):
        """
        send keyevent

        :Args:
            - keycode: keyevent code
              http://developer.android.com/reference/android/view/KeyEvent.html
        """
        cmd = "input keyevent %s" % keycode
        adb.shell(cmd)

    def tap(self,xcoord,ycoord):
        """
        Tap at given coordinates

        :Args:
            - xcoord: X Coordinate to tap
            - ycoord: Y Coordinate to tap
        """
        self._assertCoord(xcoord,ycoord)
        cmd = "input tap %s %s" % (xcoord,ycoord)
        adb.shell(cmd)

    def tapByRatio(self,xratio,yratio):
        """
        Tap at coordinates by ratio

        :Args:
            - xratio: X ratio
            - yratio: Y ratio
        """
        xcoord,ycoord = self._assertTatio(xratio,yratio)
        self.tap(xcoorc,ycoord)

    def swipe(self,xstart,ystart,xend,yend,duration=None):
        """
        Swipe

        :Args:
            - xstart: X start coordinate
            - ystart: Y start coordinate
            - xend: X end coordinate
            - yend: Y end coordinate
            - duration: android >= 4.4 can use opt duration(ms)
        """
        self._assertCoord(xstart,ystart)
        self._assertCoord(xend,yend)
        if duration:
            duration = int(duration)
        else:
            duration = ""
        cmd = "input swipe %s %s %s %s %s" % (xstart,ystart,xend,yend,duration)
        adb.shell(cmd)

    def swipeByRatio(self,start_ratio_x,start_ratio_y,end_ratio_x,end_ratio_y,duration=None):
        """
        Swipe by ratio

        :Args:
            - start_ratio_x: start X ratio
            - start_ratio_y: start Y ratio
            - end_ratio_x: end X ratio
            - end_ratio_y: end Y ratio
            - duration: android >= 4.4 can use opt duration(ms)
         """
        xstart,ystart=self.assertRatio(start_ratio_x,start_ratio_y)
        xend,yend = self.assertRatio(end_ratio_x,end_ratio_y)
        self.swipe(xstart,ystart,xend,yend,duration)

    def back(self):
        """
        Pressiong the back button

        :Usage:
            driver.adb_actions.back()
        """
        self.keyevent(Keys.BACK)

    def goToHome(self):
        """
        Pressing the HOME button
        """
        self.keyevent(Keys.HOME)

    def menu(self):
        """
        Pressing the MENU button
        """
        self.keyevnet(Keys.MENU)

    def volumeUp(self):
        """
        Pressing the volume up button
        """
        self.keyevent(Keys.VOLUME_UP)

    def volumeDown(self):
        """
        Pressing the volume down button
        """
        self.keyevent(Keys.VOLUME_DOWN)

    def swipeToLeft(self):
        """
        Swipe to left
        """
        self.swipeByRatio(0.9,0.5,0.1,0.5)

    def swipeToRight(self):
        """
        Swipe to right
        """
        self.swipeByRatio(0.1,0.5,0.9,0.5)

    def swipeToUp(self):
        """
        Swipe to up
        """
        self.swipeByRatio(0.5,0.9,0.5,0.1)

    def swipeToDown(self):
        """
        Swipe to down
        """
        self.swipeByRatio(0.5,0.1,0.5,0.9)
    
    def sendText(self,text):
        cmd = "input text \"%s\"" % text
        adb.shell(cmd)
        
    

    def assertRatio(self,ratio_x,ratio_y):
        ratio_x = float(ratio_x)
        ratio_y = float(ratio_y)
        width,height = adb.getScreenResolution()
        x = self._getCoord(ratio_x,width)
        y = self._getCoord(ratio_y,height)
        return (x,y)

    def _assertCoord(self,xcoord,ycoord):
        width,height = adb.getScreenResolution()
        x = int(xcoord)
        y = int(ycoord)
        if x > width or y > height:
            msg = "Coordinates are beyond the scope of,resolution: %s*%s,x: %s,y: %s" % (width,height,x,y)
            raise Exception(msg)
    
    def _getCoord(self,ratio,resolution):
        if 1 >= float(ratio) > 0:
            return ratio * resolution
        elif ratio <= resolution:
            return ratio
        else:
            msg = "Coordinates are beyond the scope of,ratio: %s,resolution: %s" % (ratio,resolution)
            raise Exception(msg)

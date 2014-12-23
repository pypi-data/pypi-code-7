import wx
import wx.html2

import urllib
import time
import threading
from runserver import runserver
import settings

########################################################################
class WxWebView(wx.Dialog):

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwds):
        """"""
        wx.Dialog.__init__(self, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        sizer.Add(self.browser, 1, wx.EXPAND, 10)


        # self.SetSizer(sizer)
        # self.SetSize((700, 700))

        self.wait_deploy()


        #Host
        self.load(settings.HOST)

        #Title
        self.setWindowTitle(settings.WINDOW_TITLE)

        #Maximized
        if getattr(settings, "MAXIMIZED", False):
            self.showMaximized()

        #Size
        if getattr(settings, "SIZE", False):
            if type(settings.SIZE) == type(""):
                percent = float(settings.SIZE.replace("%", "")) / 100.0
                self.resize(QtGui.QDesktopWidget().screenGeometry().size()*percent)
            else:
                self.resize(*settings.SIZE)
        else:
            self.resize(QtGui.QDesktopWidget().screenGeometry().size()/1.5)

        #Position
        if getattr(settings, "POSITION", False):
            if settings.POSITION == "CENTER":

            else:




    #----------------------------------------------------------------------
    def wait_deploy(self):
        """"""
        start = time.time()
        while True or (time.time() - start) > settings.TIMEOUT:
            try:
                urllib.urlopen(settings.HOST)
                break
            except:
                time.sleep(1)


#----------------------------------------------------------------------
def deploy():
    """"""
    threading.Thread(target=runserver, args=(settings, )).start()
    app = wx.App()
    #run GUI



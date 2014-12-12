import wx
import wx.html2

import urllib
import time
import threading
from runserver import runserver
import settings

########################################################################
class WxWebView(wx.Frame):

    #----------------------------------------------------------------------
    def __init__(self, *args, **kwds):
        """"""
        wx.Frame.__init__(self, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)

        self.wait_deploy()

        #Host
        self.browser.LoadURL(settings.HOST)

        #Title
        self.SetTitle(settings.WINDOW_TITLE)

        #Maximized
        if getattr(settings, "MAXIMIZED", False):
            self.showMaximized()

        #Size
        if getattr(settings, "SIZE", False):
            if type(settings.SIZE) == type(""):
                percent = float(settings.SIZE.replace("%", "")) / 100.0
                size = wx.Display().GetGeometry().size
                size.Scale(percent, percent)
                self.SetSize(size)
            else:
                self.SetSize(*settings.SIZE)
        else:
            size = wx.Display().GetGeometry().size
            size.Scale(1.5, 1.5)
            self.SetSize(size)

        #Position
        if getattr(settings, "POSITION", False):
            if settings.POSITION == "CENTER":
                screen = wx.Display().GetGeometry().size
                size = self.GetSize()
                self.MoveXY((screen.width-size.width)/2, (screen.height-size.height)/2)
            else:
                self.MoveXY(*settings.POSITION)


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
    dialog = WxWebView(None, -1)
    dialog.Show()
    app.MainLoop()


from PySide.QtWebKit import QWebView
from PySide import QtGui, QtCore
import sys

import urllib
import time
import threading
from runserver import runserver
import settings

########################################################################
class PySideQWebView(QWebView):

    #----------------------------------------------------------------------
    def __init__(self, parent=None):
        """"""
        super(PySideQWebView, self).__init__(parent)

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
                screen = QtGui.QDesktopWidget().screenGeometry()
                size =  self.geometry()
                self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
            else:
                self.move(*settings.POSITION)


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
    app = QtGui.QApplication(sys.argv)
    frame = PySideQWebView()
    frame.show()
    app.exec_()

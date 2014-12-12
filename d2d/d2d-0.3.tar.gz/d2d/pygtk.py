import sys
import gtk
import webkit
import gobject

import urllib
import time
import threading
from runserver import runserver
import settings

########################################################################
class GtkWebView(object):

    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        gobject.threads_init()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.connect('delete_event', self.close_application)
        self.window.set_default_size(800, 600)

        vbox = gtk.VBox()

        self.scrolled_window = gtk.ScrolledWindow(None, None)
        self.webview = webkit.WebView()
        self.scrolled_window.add(self.webview)

        vbox.pack_start(self.scrolled_window, fill=True, expand=True)


        self.wait_deploy()

        #Host
        self.webview.open(settings.HOST)

        #Title
        self.window.set_title(settings.WINDOW_TITLE)

        #Maximized
        if getattr(settings, "MAXIMIZED", False):
            self.window.maximize()

        #Size
        if getattr(settings, "SIZE", False):
            if type(settings.SIZE) == type(""):
                percent = float(settings.SIZE.replace("%", "")) / 100.0
                self.window.resize(int(gtk.gdk.Screen().get_width()*percent), int(gtk.gdk.Screen().get_height()*percent))
            else:
                self.window.resize(*settings.SIZE)
        else:
            self.window.resize(int(gtk.gdk.Screen().get_width()/1.5), int(gtk.gdk.Screen().get_height()/1.5))



        #Position
        # Centered by default


        self.window.add(vbox)
        self.window.show_all()



    def close_application(self, widget, event, data=None):
        gtk.main_quit()



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


    def main(self):
        gtk.main()

#----------------------------------------------------------------------
def deploy():
    """"""
    threading.Thread(target=runserver, args=(settings, )).start()
    browser = GtkWebView()
    browser.main()

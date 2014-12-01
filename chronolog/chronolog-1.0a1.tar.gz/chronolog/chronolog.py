#!/usr/bin/python
import gtk
import httplib
import urllib
import unirest

try:
    import wnck
except ImportError:
    print "Need python-wnck"
    exit(1)


import glib
import time
import sys, platform

try:
    import appindicator
except ImportError:
    import appindicator_replacement as appindicator

import os
import ctypes
import ctypes.util
import platform

class XScreenSaverInfo(ctypes.Structure):
    _fields_ = [('window', ctypes.c_long),
                ('state', ctypes.c_int),
                ('kind', ctypes.c_int),
                ('til_or_since', ctypes.c_ulong),
                ('idle', ctypes.c_ulong),
                ('eventMask', ctypes.c_ulong)]

class IdleXScreenSaver(object):
    def __init__(self):
        self.xss = self._get_library('Xss')
        self.gdk = self._get_library('gdk-x11-2.0')

        self.gdk.gdk_display_get_default.restype = ctypes.c_void_p
        # GDK_DISPLAY_XDISPLAY expands to gdk_x11_display_get_xdisplay
        self.gdk.gdk_x11_display_get_xdisplay.restype = ctypes.c_void_p
        self.gdk.gdk_x11_display_get_xdisplay.argtypes = [ctypes.c_void_p]
        # GDK_ROOT_WINDOW expands to gdk_x11_get_default_root_xwindow
        self.gdk.gdk_x11_get_default_root_xwindow.restype = ctypes.c_void_p

        self.xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
        self.xss.XScreenSaverQueryExtension.restype = ctypes.c_int
        self.xss.XScreenSaverQueryExtension.argtypes = [ctypes.c_void_p,
                                                        ctypes.POINTER(ctypes.c_int),
                                                        ctypes.POINTER(ctypes.c_int)]
        self.xss.XScreenSaverQueryInfo.restype = ctypes.c_int
        self.xss.XScreenSaverQueryInfo.argtypes = [ctypes.c_void_p,
                                                   ctypes.c_void_p,
                                                   ctypes.POINTER(XScreenSaverInfo)]

        # gtk_init() must have been called for this to work
        import gtk
        gtk  # pyflakes

        # has_extension = XScreenSaverQueryExtension(GDK_DISPLAY_XDISPLAY(gdk_display_get_default()),
        #                                            &event_base, &error_base);
        event_base = ctypes.c_int()
        error_base = ctypes.c_int()
        gtk_display = self.gdk.gdk_display_get_default()
        self.dpy = self.gdk.gdk_x11_display_get_xdisplay(gtk_display)
        available = self.xss.XScreenSaverQueryExtension(self.dpy,
                                                        ctypes.byref(event_base),
                                                        ctypes.byref(error_base))
        if available == 1:
            self.xss_info = self.xss.XScreenSaverAllocInfo()
        else:
            self.xss_info = None

    def _get_library(self, libname):
        path = ctypes.util.find_library(libname)
        if not path:
            raise ImportError('Could not find library "%s"' % (libname, ))
        lib = ctypes.cdll.LoadLibrary(path)
        assert lib
        return lib

    def get_idle(self):
        if not self.xss_info:
            return 0

        # XScreenSaverQueryInfo(GDK_DISPLAY_XDISPLAY(gdk_display_get_default()),
        #                       GDK_ROOT_WINDOW(), mit_info);
        drawable = self.gdk.gdk_x11_get_default_root_xwindow()
        self.xss.XScreenSaverQueryInfo(self.dpy, drawable, self.xss_info)
        # return (mit_info->idle) / 1000;
        return self.xss_info.contents.idle

idle = IdleXScreenSaver()

class EntryDialog(gtk.MessageDialog):
    def __init__(self, *args, **kwargs):
        '''
        Creates a new EntryDialog. Takes all the arguments of the usual
        MessageDialog constructor plus one optional named argument
        "default_value" to specify the initial contents of the entry.
        '''
        if 'default_value' in kwargs:
            default_value = kwargs['default_value']
            del kwargs['default_value']
        else:
            default_value = ''
        super(EntryDialog, self).__init__(*args, **kwargs)
        entry = gtk.Entry()
        entry.set_text(str(default_value))
        entry.connect("activate",
            lambda ent, dlg, resp: dlg.response(resp),
            self, gtk.RESPONSE_OK)
        self.vbox.pack_end(entry, True, True, 0)
        self.vbox.show_all()
        self.entry = entry
    def set_value(self, text):
        self.entry.set_text(text)
    def run(self):
        result = super(EntryDialog, self).run()
        if result == gtk.RESPONSE_OK:
            text = self.entry.get_text()
        else:
            text = None
        return text

class WindowTitle(object):
    def __init__(self, ind):
        self.title = None
        self.lastMousePos = None
        self.lastMouseMoveTime = None
        self.lastKeyPressTime = None
        self.active = True
        self.idleTime = 300000
        self.changesRecorded = 0
        self.lastSend = 0

        self.userCode = None
        try:
            file = open(os.path.expanduser('~')+'/.chronolog', 'r+');
            self.userCode = file.readline().strip('\n')
            file.close()
        except:
            pass


        # create a menu
        menu = gtk.Menu()

        # create some

        self.statusMenu = gtk.MenuItem("Active")
        self.codeMenu = gtk.MenuItem("Set User Code")
        self.exitMenu = gtk.MenuItem("Exit")


        sep = gtk.SeparatorMenuItem();
        menu.append(self.statusMenu)
        menu.append(self.codeMenu)
        menu.append(sep)
        menu.append(self.exitMenu)


        # this is where you would connect your menu item up with a function:

        self.exitMenu.connect("activate", self.exit, "Test")
        self.codeMenu.connect("activate", self.setCode, "Test")

        # show the items
        self.statusMenu.show()
        self.codeMenu.show()
        self.exitMenu.show()
        sep.show()

        ind.set_menu(menu)
        print "finished with menu"

        glib.timeout_add(1000, self.get_title)


    def exit(self, w, buf):
        sys.exit(0)

    def setCode(self, w, buff):
        print "dialog"
        dialog = EntryDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK_CANCEL, "Set User Code", default_value=self.userCode)
        dialog.show_all()
        result = dialog.run()
        print "done"
        dialog.destroy()
        self.userCode = result
        configFile = open(os.path.expanduser('~')+'/.chronolog','w')
        configFile.write(self.userCode)
        configFile.close()

    def callback_function(self, response):
        print str(response.code) + ": " + response.raw_body

    def writelog(self, time, app, title, idle):
        hostname = platform.node()
        print "posting "+app+" - "+title+" as "+str(self.userCode)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        params = {'Host': hostname, 'Time': time, 'Idle': idle, 'Process': app, 'Title': title, 'UserCode': self.userCode, "Client": 'Unix'}
        thread = unirest.post("https://chronolog.us/register", headers=headers, params=params, callback=self.callback_function)

    def get_title(self):
        try:
            now = time.time()
            idletime = idle.get_idle()

            title = wnck.screen_get_default().get_active_window().get_name()
            app = str(wnck.screen_get_default().get_active_window().get_application().get_pid())
            file = open('/proc/'+app+'/comm');
            name = file.readline().strip('\n')
            file.close()

            print "Idle time in milliseconds: %d" % ( idletime )
            #print self.lastMouseMoveTime, time.time()
            if idletime > self.idleTime and self.active == True:
                self.active = False
                self.statusMenu.set_label("Idle")
                self.writelog(now, name, title, self.active)
            elif self.active == False and idletime < self.idleTime:
                self.active = True
                self.statusMenu.set_label("Active - "+str(self.changesRecorded)+' activities recorded')
                self.writelog(now, name, title, self.active)

            if self.title != title or now - self.lastSend > self.idleTime/1000 :
                self.title  = title
                self.changesRecorded+=1
                self.statusMenu.set_label("Active - "+str(self.changesRecorded)+' activities recorded')
                self.writelog(now, name, title, self.active)
                self.lastSend = time.time();

        except AttributeError:
            pass
        return True

def start():
    print "indicator"
    icon_image = os.path.dirname(os.path.realpath(__file__)) + "/../images/chronolog_inverse.png"
    print icon_image
    ind = appindicator.Indicator ("chronolog",
        icon_image,
        appindicator.CATEGORY_APPLICATION_STATUS)
    ind.set_status(appindicator.STATUS_ACTIVE)


    print "title"
    title = WindowTitle(ind)

    gtk.main()

    exit(0)

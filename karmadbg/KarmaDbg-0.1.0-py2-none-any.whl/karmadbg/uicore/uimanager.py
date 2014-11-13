
import sys
import os

from itertools import ifilter

from PySide.QtCore import *
from PySide.QtGui import QMainWindow, QFileDialog, QAction, QKeySequence

from karmadbg.dbgcore.settings import DbgSettings
from karmadbg.uicore.dbgclient import DebugClient, DebugAsyncCall
from karmadbg.uicore.defaultstyle import defaultStyle

class UIManager(QObject):

    outputRequired = Signal(str)
    inputRequired = Signal()
    inputCompleted = Signal()

    targetRunning = Signal()
    targetStopped = Signal()
    targetDetached = Signal()
    targetDataChanged = Signal()

    pythonRunning = Signal()
    pythonStopped = Signal()
    pythonExit = Signal()
    pythonDataChanged = Signal()
    pythonBreakpointAdded = Signal(str,int)
    pythonBreakpointRemoved = Signal(str,int)

    def __init__(self, app):
        super(UIManager,self).__init__()

        self.app = app
    
        import karmadbg
        dirname = os.path.dirname(karmadbg.__file__)
        filename = os.path.join( dirname, "settings", "default.xml" )
        self.dbgSettings = DbgSettings(filename)
        self.workspace = self.dbgSettings.workspaces[0]
        self.mainwnd = MainForm(self.workspace.mainWindow)

        if self.workspace.style:
            if self.workspace.style.fileName:
                filename = os.path.join( dirname, self.workspace.style.fileName )
                with open(filename) as file:
                    style = reduce( lambda x,y: x + y, file)
                    self.mainwnd.setStyleSheet(style)
            else:
                if self.workspace.style.text:
                    self.mainwnd.setStyleSheet(self.workspace.style.text)
                else:
                    self.mainwnd.setStyleSheet(defaultStyle)
        else:
             self.mainwnd.setStyleSheet(defaultStyle)

        self.actions = ActionManager(self.workspace, self)
        self.widgets = WidgetManager(self.workspace, self)
        self.dialogs = DialogManager(self.workspace, self)
        self.mainMenu = getMainMenuManager(self.workspace.mainMenu, self)

        #sys.stdout = self
        self.debugClient = DebugClient(self, self.workspace)
        self.debugClient.start()

        self.app.aboutToQuit.connect(self.onQuit)
        self.mainwnd.show()

    def write(self,str):
        self.outputRequired.emit(str)

    def onQuit(self):
        self.debugClient.stop()

    def quit(self):
        self.mainwnd.close()

    def openProcess(self):
        if "OpenProcess" in self.dialogs:
            processName = self.dialogs["OpenProcess"].getProcessName()
        else:
            processName = QFileDialog().getOpenFileName()[0]

        if processName:
            self.debugClient.openProcess(processName)

    def openDump(self):
        if "OpenDump" in self.dialogs:
            fileName = self.dialogs["OpenDump"].getFileName()
        else:
            fileName = QFileDialog().getOpenFileName()[0]

        if fileName:
            self.debugClient.openDump(fileName)

    def inputComplete(self,str):
        self.debugClient.inputCompleted.emit(str)


    def getWidget(self, name):
        if name in self.widgets:
            return self.widgets[name]

    def getDialog(self, name):
        if name in self.dialogs:
            return self.dialogs[name]

    def toggleWidget(self, name):
        widget = self.getWidget(name)
        if widget:
            widget.setVisible( widget.isVisible() == False )

    def callFunction(self, *args, **kwargs):
        return self.debugClient.callFunction(*args,**kwargs)

class MainForm(QMainWindow):

    def __init__(self, settings):
        super(MainForm,self).__init__(None)

        self.resize(settings.width, settings.height)
        self.setWindowTitle(settings.title)
        self.setDockNestingEnabled(True)


def getMainMenuManager(dbgsettings,uimanager):
    module = __import__( dbgsettings.module, fromlist=[dbgsettings.className])
    classobj = getattr(module, dbgsettings.className)
    return classobj(dbgsettings, uimanager)

class WidgetManager(QObject):

    def __init__(self, dbgsettings, uimanager):
        
        super(WidgetManager,self).__init__()

        self.uimanager = uimanager
        self.widgets = {}

        for widgetSetting in dbgsettings.widgets:
            self.widgets[ widgetSetting.name ] = self.constructWidget(widgetSetting)

    def constructWidget(self, widgetSettings):
        module = __import__( widgetSettings.module, fromlist=[widgetSettings.className])
        classobj = getattr(module, widgetSettings.className)
        obj = classobj(widgetSettings, self.uimanager)
        obj.behaviour = widgetSettings.behaviour
        obj.setVisible(widgetSettings.visible)
        if hasattr(obj, "constructDone"): obj.constructDone()
        if widgetSettings.title:
            obj.setWindowTitle(widgetSettings.title)
        return obj

    def __getitem__(self,name):
        return self.widgets[name]

    def __contains__(self,name):
        return name in self.widgets

    def values(self):
        return self.widgets.values()


class DialogManager(QObject):

    def __init__(self, dbgsettings, uimanager):
        
        super(DialogManager,self).__init__()

        self.uimanager = uimanager
        self.dialogs = {}

        for dialogSetting in dbgsettings.dialogs:
            self.dialogs[ dialogSetting.name ] = self.constructDialog(dialogSetting)

    def constructDialog(self, dialogSetting):
        module = __import__( dialogSetting.module, fromlist=[dialogSetting.className])
        classobj = getattr(module, dialogSetting.className)
        return classobj(dialogSetting, self.uimanager)

    def __getitem__(self,name):
        return self.dialogs[name]

    def __contains__(self,name):
        return name in self.dialogs

class ActionManager(QObject):

    def __init__(self,dbgsettings, uimanager):
        super(ActionManager, self).__init__()
        self.uimanager = uimanager
        self.actions = {}

        for actionSetting in dbgsettings.actions:
            self.actions[ actionSetting.name ] = self.constructAction(actionSetting)

    def __getitem__(self,name):
        if name in self.actions:
            return self.actions[name]
        return QAction(name,self.uimanager.mainwnd)

    def __contains__(self,name):
        return name in self.actions

    def constructAction(self,actionSetting):
        
        action = QAction(actionSetting.displayName,self.uimanager.mainwnd)
        if actionSetting.shortcut: 
            action.setShortcut(QKeySequence(actionSetting.shortcut))

        if actionSetting.module and actionSetting.funcName:
            module = __import__(actionSetting.module, fromlist=[actionSetting.funcName])
            funcobj = getattr(module, actionSetting.funcName)
            action.triggered.connect(lambda : funcobj(self.uimanager) )

        if actionSetting.toggleWidget:
            action.triggered.connect(lambda : self.uimanager.toggleWidget(actionSetting.toggleWidget))

        if actionSetting.showDialog:
            action.triggered.connect(lambda : self.uimanager.showDialog(actionSettings.showDialog))

        return action




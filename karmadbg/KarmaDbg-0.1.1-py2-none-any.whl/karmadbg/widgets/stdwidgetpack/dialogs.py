from PySide.QtGui import QFileDialog

class OpenProcessDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenProcessDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager
        self.setNameFilter( "Executable (*.exe)" )

    def getProcessName(self):
        return self.getOpenFileName()[0]


class OpenDumpDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenDumpDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager

    def getFileName(self):
        return self.getOpenFileName()[0]


class OpenSourceDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenSourceDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager

    def getFileName(self):
        return self.getOpenFileName()[0]
